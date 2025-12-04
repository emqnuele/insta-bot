import re
from typing import Optional

from ai_client import AIClient
from ig_client import IncomingMessage
from state_store import StateStore


class MessageRouter:
    def __init__(self, ai_client: AIClient, state_store: StateStore, logger):
        self.ai_client = ai_client
        self.state_store = state_store
        self.logger = logger

    def handle_incoming(self, message: IncomingMessage) -> Optional[str]:
        if not message.text or not message.text.strip():
            self.logger.debug("Skipping empty message %s", message.message_id)
            return None

        if self._is_link_only(message.text):
            self.logger.info("Skipping link-only message from %s", message.user_id)
            return None

        lowered = message.text.strip().lower()
        if lowered == "/start":
            return "Hi! I'm an automatic reply bot for Instagram.\n\nIf you need help, write to me!"

        reply = self.ai_client.generate_reply(message.text, message.user_id, message.username)
        self.logger.debug("AI produced reply for %s", message.message_id)
        return reply

    def _is_link_only(self, text: str) -> bool:
        text = text.strip()
        url_pattern = re.compile(r"https?://\S+")
        return bool(url_pattern.fullmatch(text))
