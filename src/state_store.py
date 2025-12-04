import json
import threading
from pathlib import Path
from typing import Set


class StateStore:
    def __init__(self, path: str, logger):
        self.path = Path(path)
        self.logger = logger
        self.processed_ids: Set[str] = set()
        self.lock = threading.Lock()

    def load(self) -> None:
        if not self.path.exists():
            self.logger.info("State file not found, starting fresh")
            return

        try:
            data = json.loads(self.path.read_text())
        except json.JSONDecodeError:
            self.logger.warning("State file is corrupted, starting fresh")
            return

        processed = data.get("processed_ids", [])
        if isinstance(processed, list):
            self.processed_ids = set(processed)
        self.logger.info("Loaded %d processed message IDs", len(self.processed_ids))

    def has_processed(self, message_id: str) -> bool:
        # Reading is generally safe without lock if set operations are atomic, 
        # but for strict correctness we could lock. 
        # Given the usage pattern, we mostly care about write safety.
        return message_id in self.processed_ids

    def mark_processed(self, message_id: str) -> None:
        with self.lock:
            self.processed_ids.add(message_id)
            self._save()

    def _save(self) -> None:
        # _save is called within the lock from mark_processed
        self.path.parent.mkdir(parents=True, exist_ok=True)
        data = {"processed_ids": sorted(self.processed_ids)}
        self.path.write_text(json.dumps(data, indent=2))
        self.logger.debug("State saved with %d IDs", len(self.processed_ids))
