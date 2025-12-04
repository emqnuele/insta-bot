import sys
import os
from pathlib import Path
import logging

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ai_client import AIClient
from history_store import HistoryStore
from config import Settings

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("test_genai")

def test_integration():
    # Mock settings
    settings = Settings(
        ig_username="test_user",
        ig_password="test_password",
        ai_api_key=os.getenv("AI_API_KEY") or os.getenv("GOOGLE_API_KEY"), # Try both
        ai_model_name="gemini-2.0-flash",
        poll_interval_seconds=5
    )
    
    if not settings.ai_api_key:
        logger.error("No API key found in environment variables (AI_API_KEY or GOOGLE_API_KEY).")
        return

    # Initialize store and client
    history_store = HistoryStore(data_dir="data/test_history")
    client = AIClient(settings, logger, history_store)

    user_id = "test_user_123"
    
    # Test message 1
    logger.info("Sending message 1...")
    reply1 = client.generate_reply("Ciao, come ti chiami?", user_id)
    logger.info(f"Reply 1: {reply1}")
    
    # Test message 2 (context)
    logger.info("Sending message 2...")
    reply2 = client.generate_reply("Qual è il mio nome? (Dovresti saperlo se sei un gatto)", user_id)
    logger.info(f"Reply 2: {reply2}")

    # Verify history
    history = history_store.get_history(user_id)
    logger.info(f"History length: {len(history)}")
    logger.info(f"History content: {history}")

if __name__ == "__main__":
    test_integration()
