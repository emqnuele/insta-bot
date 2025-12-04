from typing import Optional
from pathlib import Path
from google import genai
from google.genai import types

from config import Settings
from history_store import HistoryStore

class AIClient:
    def __init__(self, settings: Settings, logger, history_store: HistoryStore):
        self.settings = settings
        self.logger = logger
        self.history_store = history_store
        self.client = genai.Client(api_key=settings.ai_api_key)
        self.system_instruction = self._load_system_instruction()

    def _load_system_instruction(self) -> str:
        try:
            return Path("system_instruction.txt").read_text(encoding="utf-8").strip()
        except Exception as e:
            self.logger.error(f"Failed to load system instruction: {e}")
            return "You are a helpful assistant."

    def generate_reply(self, user_message: str, user_id: str, username: Optional[str] = None) -> str:
        """Generate a reply using the configured AI model."""
        
        # Add user message to history
        self.history_store.add_message(user_id, "user", user_message)
        
        # Get history for context
        raw_history = self.history_store.get_history(user_id, limit=25)
        
        # Convert history to types.Content objects
        contents = []
        for item in raw_history:
            parts = []
            for part in item.get("parts", []):
                if isinstance(part, str):
                    parts.append(types.Part(text=part))
                # Handle other part types if necessary (e.g. images)
            contents.append(types.Content(role=item["role"], parts=parts))
        
        try:
            response = self.client.models.generate_content(
                model=self.settings.ai_model_name,
                config=types.GenerateContentConfig(
                    system_instruction=self.system_instruction,
                    temperature=0.7,
                ),
                contents=contents
            )
            
            reply = response.text.strip()
            self.logger.debug("AI reply generated: %s", reply)
            
            # Add model response to history
            self.history_store.add_message(user_id, "model", reply)
            
            return reply
            
        except Exception as e:
            self.logger.error(f"Error generating content: {e}")
            return "Sorry, I'm having trouble processing your request right now."

