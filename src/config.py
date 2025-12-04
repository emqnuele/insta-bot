from dataclasses import dataclass
from os import getenv
from typing import Optional

from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    ig_username: str
    ig_password: str
    ai_api_key: str
    ai_model_name: str
    poll_interval_seconds: int = 5
    proxy_url: Optional[str] = None
    session_file: str = "data/sessions/ig_session.json"
    state_file: str = "data/state.json"


class MissingConfiguration(Exception):
    """Raised when required configuration is missing."""


def get_settings() -> Settings:
    settings = Settings(
        ig_username=getenv("IG_USERNAME", ""),
        ig_password=getenv("IG_PASSWORD", ""),
        ai_api_key=getenv("AI_API_KEY", ""),
        ai_model_name=getenv("AI_MODEL_NAME", "gpt-4.1-mini"),
        poll_interval_seconds=int(getenv("POLL_INTERVAL_SECONDS", "5")),
        proxy_url=getenv("PROXY_URL") or None,
    )

    _validate(settings)
    return settings


def _validate(settings: Settings) -> None:
    missing = [
        name
        for name, value in {
            "IG_USERNAME": settings.ig_username,
            "IG_PASSWORD": settings.ig_password,
            "AI_API_KEY": settings.ai_api_key,
        }.items()
        if not value
    ]

    if missing:
        raise MissingConfiguration(
            "Missing required configuration variables: " + ", ".join(missing)
        )
