import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from instagrapi import Client

from config import Settings


@dataclass
class IncomingMessage:
    message_id: str
    user_id: str
    username: Optional[str]
    text: str
    timestamp: datetime


class InstagramClient:
    def __init__(self, settings: Settings, logger):
        self.settings = settings
        self.logger = logger
        self.client = Client()
        # Set startup time to ignore old messages (UTC to match instagrapi usually)
        self.start_time = datetime.now().astimezone()
        
        if settings.proxy_url:
            self.logger.info("Using proxy: %s", settings.proxy_url)
            self.client.set_proxy(settings.proxy_url)
        self.session_path = Path(settings.session_file)

    def login(self) -> None:
        if self.session_path.exists():
            self.logger.info("Loading existing Instagram session")
            settings_data = json.loads(self.session_path.read_text())
            self.client.set_settings(settings_data)

        self.logger.info("Logging into Instagram as %s", self.settings.ig_username)
        self.client.login(self.settings.ig_username, self.settings.ig_password)
        self.session_path.parent.mkdir(parents=True, exist_ok=True)
        self.session_path.write_text(json.dumps(self.client.get_settings()))
        self.logger.info("Instagram login successful; session saved at %s", self.session_path)

    def fetch_new_messages(self, amount: int = 20) -> List[IncomingMessage]:
        threads = self.client.direct_threads(amount=amount)
        incoming: List[IncomingMessage] = []
        for thread in threads:
            for item in thread.messages:
                # Robustly check if message is from self
                if str(item.user_id) == str(self.client.user_id):
                    continue
                
                # Filter out messages sent before bot startup
                # Ensure item.timestamp is aware for comparison
                msg_time = item.timestamp
                if msg_time.tzinfo is None:
                    msg_time = msg_time.astimezone()
                
                if msg_time < self.start_time:
                    continue

                text = getattr(item, "text", None)
                if not text:
                    continue
                incoming.append(
                    IncomingMessage(
                        message_id=item.id,
                        user_id=str(item.user_id),
                        username=getattr(item, "user", None).username if getattr(item, "user", None) else None,
                        text=text,
                        timestamp=item.timestamp,
                    )
                )

        incoming.sort(key=lambda msg: msg.timestamp)
        if incoming:
            self.logger.debug("Fetched %d incoming messages", len(incoming))
        return incoming

    def send_message(self, user_id: str, text: str) -> None:
        self.client.direct_send(text, [user_id])
        self.logger.info("Sent reply to user %s", user_id)
