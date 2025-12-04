import time
import logging
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_batching")

@dataclass
class MockMessage:
    message_id: str
    user_id: str
    text: str

def test_batching_logic():
    BATCH_WINDOW = 2.0
    message_buffer = {}
    
    def ingest(msg):
        if msg.user_id not in message_buffer:
            message_buffer[msg.user_id] = {'messages': [], 'last_received': 0}
        
        message_buffer[msg.user_id]['messages'].append(msg)
        message_buffer[msg.user_id]['last_received'] = time.time()
        logger.info(f"Buffered: {msg.text}")

    def process():
        current_time = time.time()
        users_to_process = []
        for user_id, buffer in message_buffer.items():
            if buffer['messages'] and (current_time - buffer['last_received'] > BATCH_WINDOW):
                users_to_process.append(user_id)
        
        for user_id in users_to_process:
            msgs = message_buffer[user_id]['messages']
            full_text = "\n".join([m.text for m in msgs])
            logger.info(f"PROCESSED BATCH for {user_id}: {full_text.replace('\n', ' + ')}")
            del message_buffer[user_id]

    # Simulate
    logger.info("--- Start Simulation ---")
    
    # User A sends "Ciao"
    ingest(MockMessage("1", "userA", "Ciao"))
    process() # Should do nothing yet
    
    time.sleep(1.0)
    
    # User A sends "Come stai?" (within window)
    ingest(MockMessage("2", "userA", "Come stai?"))
    process() # Should still do nothing (window reset)
    
    time.sleep(1.0)
    process() # Still waiting...
    
    time.sleep(1.5) # Now total time > 2.0 from last message
    process() # Should process batch

if __name__ == "__main__":
    test_batching_logic()
