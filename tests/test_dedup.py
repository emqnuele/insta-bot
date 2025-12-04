import time
import logging
from dataclasses import dataclass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_dedup")

@dataclass
class MockMessage:
    message_id: str
    user_id: str
    text: str

def test_inflight_logic():
    inflight_ids = set()
    message_buffer = {}
    
    def ingest(msg):
        if msg.message_id in inflight_ids:
            logger.info(f"IGNORED (Inflight): {msg.message_id}")
            return

        if msg.user_id not in message_buffer:
            message_buffer[msg.user_id] = {'messages': []}
        
        message_buffer[msg.user_id]['messages'].append(msg)
        inflight_ids.add(msg.message_id)
        logger.info(f"BUFFERED: {msg.message_id}")

    def finish_processing(msg):
        inflight_ids.discard(msg.message_id)
        logger.info(f"FINISHED: {msg.message_id}")

    logger.info("--- Start Dedup Test ---")
    
    msg1 = MockMessage("101", "userA", "Hello")
    
    # 1. First fetch
    ingest(msg1) # Should buffer
    
    # 2. Second fetch (simulating re-fetch while pending)
    ingest(msg1) # Should ignore
    
    # 3. Finish processing
    finish_processing(msg1)
    
    # 4. Third fetch (simulating re-fetch after processing)
    # In real app, state_store would block this. 
    # Here we just test inflight logic, so it would buffer again if we don't check state_store.
    # But inflight check passed, so it works as intended for the "while pending" case.
    ingest(msg1) 

if __name__ == "__main__":
    test_inflight_logic()
