import random
import time

from ai_client import AIClient
from config import MissingConfiguration, get_settings
from ig_client import InstagramClient
from logger import get_logger
from message_router import MessageRouter
from state_store import StateStore
from history_store import HistoryStore


MIN_DELAY_SECONDS = 3
MAX_DELAY_SECONDS = 20


import concurrent.futures

def process_reply_task(user_id, combined_msg, original_msgs, router, ig_client, state_store, logger, inflight_ids):
    """
    Task to be executed in a separate thread.
    Handles generating the reply, simulating typing delay, sending the message,
    and marking messages as processed.
    """
    try:
        logger.info("Processing scheduled batch for %s", user_id)
        reply = router.handle_incoming(combined_msg)
        
        if reply:
            parts = [p.strip() for p in reply.split("\n") if p.strip()]
            
            for part in parts:
                typing_delay = min(5.0, max(1.0, len(part) * 0.05 + random.uniform(0.5, 1.5)))
                logger.debug("Typing delay %.1f seconds before sending part to %s", typing_delay, user_id)
                time.sleep(typing_delay)
                ig_client.send_message(user_id, part)

        for m in original_msgs:
            state_store.mark_processed(m.message_id)
            
    except Exception as e:
        logger.exception("Error processing reply task for user %s: %s", user_id, e)
    finally:
        # Remove from inflight_ids so they don't get stuck if something fails
        # But since they are marked processed (hopefully), they won't be picked up again
        # If mark_processed failed, they might be picked up again, which is safer than losing them
        for m in original_msgs:
            inflight_ids.discard(m.message_id)


def main() -> None:
    logger = get_logger()
    try:
        settings = get_settings()
    except MissingConfiguration as exc:
        logger.error("%s", exc)
        return

    state_store = StateStore(settings.state_file, logger)
    state_store.load()
    
    history_store = HistoryStore()

    ai_client = AIClient(settings, logger, history_store)
    router = MessageRouter(ai_client, state_store, logger)
    ig_client = InstagramClient(settings, logger)
    ig_client.login()

    logger.info(
        "Bot started, polling every %s seconds (random delay %s-%s before replies)",
        settings.poll_interval_seconds,
        MIN_DELAY_SECONDS,
        MAX_DELAY_SECONDS,
    )

    BATCH_WINDOW = 10.0  # Seconds to wait for more messages
    message_buffer = {}  # {user_id: {'messages': [msg], 'last_received': timestamp}}
    pending_replies = {} # {user_id: {'time': timestamp, 'message': combined_msg}}
    inflight_ids = set() # Set of message_ids currently being handled
    
    # Thread pool for handling replies concurrently
    # Max workers = 5 means we can "type" to 5 people at once
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

    while True:
        try:
            # 1. Fetch and Buffer
            messages = ig_client.fetch_new_messages()
            for msg in messages:
                if state_store.has_processed(msg.message_id):
                    continue
                
                if msg.message_id in inflight_ids:
                    continue
                
                if msg.user_id not in message_buffer:
                    message_buffer[msg.user_id] = {
                        'messages': [],
                        'last_received': 0
                    }
                
                # Add to buffer if not already there (deduplication check)
                if not any(m.message_id == msg.message_id for m in message_buffer[msg.user_id]['messages']):
                    message_buffer[msg.user_id]['messages'].append(msg)
                    message_buffer[msg.user_id]['last_received'] = time.time()
                    inflight_ids.add(msg.message_id)
                    logger.info("Buffered message from %s: %s", msg.user_id, msg.text)

            # 2. Process Buffers -> Schedule Replies
            current_time = time.time()
            users_to_process = []

            for user_id, buffer in message_buffer.items():
                if buffer['messages'] and (current_time - buffer['last_received'] > BATCH_WINDOW):
                    users_to_process.append(user_id)

            for user_id in users_to_process:
                buffer = message_buffer[user_id]
                msgs = buffer['messages']
                
                # Combine messages
                full_text = "\n".join([m.text for m in msgs])
                latest_msg = msgs[-1]
                
                combined_msg = latest_msg
                combined_msg.text = full_text
                
                # Check if there is already a pending reply for this user
                if user_id in pending_replies:
                    # Merge with existing pending reply
                    existing = pending_replies[user_id]
                    existing['message'].text += "\n" + combined_msg.text
                    existing['original_msgs'].extend(msgs)
                    logger.info("Merged new messages into pending reply for %s. Schedule remains: %.1fs", 
                                user_id, existing['time'] - current_time)
                else:
                    # Calculate Realistic Delay
                    last_interaction = history_store.get_last_interaction_time(user_id)
                    from delay_logic import calculate_reply_delay
                    delay = calculate_reply_delay(last_interaction)
                    
                    scheduled_time = current_time + delay
                    pending_replies[user_id] = {
                        'time': scheduled_time,
                        'message': combined_msg,
                        'original_msgs': msgs
                    }
                    
                    logger.info("Scheduled reply for %s in %.1f seconds", user_id, delay)
                
                # Clear buffer
                del message_buffer[user_id]

            # 3. Process Pending Replies (Submit to Thread Pool)
            users_to_reply = []
            for user_id, pending in pending_replies.items():
                if current_time >= pending['time']:
                    users_to_reply.append(user_id)
            
            for user_id in users_to_reply:
                pending = pending_replies[user_id]
                
                # Submit task to executor
                executor.submit(
                    process_reply_task,
                    user_id,
                    pending['message'],
                    pending['original_msgs'],
                    router,
                    ig_client,
                    state_store,
                    logger,
                    inflight_ids
                )
                
                del pending_replies[user_id]

            time.sleep(settings.poll_interval_seconds)
        except Exception as exc:  # noqa: BLE001 - top-level protection
            logger.exception("Error during polling loop: %s", exc)
            time.sleep(settings.poll_interval_seconds)


if __name__ == "__main__":
    main()
