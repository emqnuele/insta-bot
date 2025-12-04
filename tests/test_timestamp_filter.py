import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from ig_client import InstagramClient
from config import Settings

class TestTimestampFilter(unittest.TestCase):
    def setUp(self):
        self.settings = MagicMock(spec=Settings)
        self.settings.proxy_url = None
        self.settings.session_file = "data/test_session.json"
        self.settings.ig_username = "test_user"
        self.settings.ig_password = "test_password"
        self.logger = MagicMock()

    @patch("ig_client.Client")
    def test_fetch_new_messages_filters_old(self, MockClient):
        # Setup client mock
        mock_instagrapi = MockClient.return_value
        mock_instagrapi.user_id = "12345" # Bot ID

        # Initialize InstagramClient
        client = InstagramClient(self.settings, self.logger)
        
        # Define start time (it's set in __init__)
        start_time = client.start_time
        
        # Create timestamps
        old_time = start_time - timedelta(minutes=10)
        new_time = start_time + timedelta(minutes=1)
        
        # Mock messages
        # Message 1: Old (should be ignored)
        msg1 = MagicMock()
        msg1.id = "msg1"
        msg1.user_id = "67890" # Other user
        msg1.text = "Old message"
        msg1.timestamp = old_time
        msg1.user = MagicMock()
        msg1.user.username = "user1"

        # Message 2: New (should be kept)
        msg2 = MagicMock()
        msg2.id = "msg2"
        msg2.user_id = "67890"
        msg2.text = "New message"
        msg2.timestamp = new_time
        msg2.user = MagicMock()
        msg2.user.username = "user1"
        
        # Message 3: From bot (should be ignored)
        msg3 = MagicMock()
        msg3.id = "msg3"
        msg3.user_id = "12345" # Bot ID
        msg3.text = "Bot message"
        msg3.timestamp = new_time
        
        # Mock threads response
        thread = MagicMock()
        thread.messages = [msg1, msg2, msg3]
        mock_instagrapi.direct_threads.return_value = [thread]

        # Execute
        incoming = client.fetch_new_messages()

        # Assertions
        self.assertEqual(len(incoming), 1)
        self.assertEqual(incoming[0].message_id, "msg2")
        self.assertEqual(incoming[0].text, "New message")
        
        print(f"Start time: {start_time}")
        print(f"Old msg time: {old_time} (Filtered: {msg1.timestamp < start_time})")
        print(f"New msg time: {new_time} (Filtered: {msg2.timestamp < start_time})")

if __name__ == "__main__":
    unittest.main()
