import json
from pathlib import Path
from typing import List, Dict, Any

class HistoryStore:
    def __init__(self, data_dir: str = "data/history"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_user_file(self, user_id: str) -> Path:
        return self.data_dir / f"{user_id}.json"

    def get_history(self, user_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        file_path = self._get_user_file(user_id)
        if not file_path.exists():
            return []
        
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
            return data[-limit:]
        except (json.JSONDecodeError, Exception):
            return []

    def get_last_interaction_time(self, user_id: str) -> Any:
        # Returns a datetime object or None
        history = self.get_history(user_id, limit=1)
        if not history:
            return None
        
        last_msg = history[-1]
        ts_str = last_msg.get("timestamp")
        if ts_str:
            from datetime import datetime
            return datetime.fromisoformat(ts_str)
        return None

    def add_message(self, user_id: str, role: str, content: str) -> None:
        file_path = self._get_user_file(user_id)
        history = []
        
        if file_path.exists():
            try:
                history = json.loads(file_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                history = []
        
        from datetime import datetime
        # Store timestamp in ISO format
        msg_data = {
            "role": role, 
            "parts": [content],
            "timestamp": datetime.now().isoformat()
        }
        history.append(msg_data)
        
        file_path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
