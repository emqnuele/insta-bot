import time
import concurrent.futures
import threading
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger("test_concurrency")

def mock_process_reply_task(user_id, duration):
    logger.info(f"START processing for {user_id} (duration {duration}s)")
    time.sleep(duration)
    logger.info(f"FINISH processing for {user_id}")

def test_concurrency():
    logger.info("--- Start Concurrency Test ---")
    
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
    
    # Submit 3 tasks that take 2 seconds each
    # If sequential, total time would be 6s
    # If concurrent, total time should be ~2s
    
    start_time = time.time()
    
    futures = []
    futures.append(executor.submit(mock_process_reply_task, "UserA", 2.0))
    futures.append(executor.submit(mock_process_reply_task, "UserB", 2.0))
    futures.append(executor.submit(mock_process_reply_task, "UserC", 2.0))
    
    # Wait for all to complete
    concurrent.futures.wait(futures)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info(f"Total time: {total_time:.2f}s")
    
    if total_time < 3.0:
        logger.info("SUCCESS: Tasks ran concurrently!")
    else:
        logger.error("FAILURE: Tasks ran sequentially!")

if __name__ == "__main__":
    test_concurrency()
