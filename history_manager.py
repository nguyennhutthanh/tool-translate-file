"""history_manager.py — persist translation history to disk."""
import json
from datetime import datetime
from pathlib import Path

HISTORY_PATH = Path.home() / ".file_translator_history.json"
MAX_ENTRIES  = 200


class HistoryManager:
    def load(self) -> list[dict]:
        if HISTORY_PATH.exists():
            try:
                return json.loads(HISTORY_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        return []

    def add(self, filename: str, source_lang: str, target_lang: str,
            provider: str, char_count: int) -> None:
        entries = self.load()
        entries.insert(0, {
            "timestamp":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "filename":    filename,
            "source_lang": source_lang,
            "target_lang": target_lang,
            "provider":    provider,
            "char_count":  char_count,
        })
        HISTORY_PATH.write_text(
            json.dumps(entries[:MAX_ENTRIES], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def clear(self) -> None:
        HISTORY_PATH.write_text("[]", encoding="utf-8")
