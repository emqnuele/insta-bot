import logging
from typing import Optional


def get_logger(name: str = "instabot", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler()
        fmt = "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
        handler.setFormatter(logging.Formatter(fmt))
        logger.addHandler(handler)
    return logger


def configure_logging(level: Optional[int] = None) -> logging.Logger:
    """Convenience helper to get a configured root logger."""
    if level is None:
        level = logging.INFO
    return get_logger(level=level)
