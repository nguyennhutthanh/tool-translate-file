"""glossary_manager.py — load/save/apply custom translation glossary."""
import json
from pathlib import Path

GLOSSARY_PATH = Path.home() / ".file_translator_glossary.json"


class GlossaryManager:
    def __init__(self) -> None:
        self._terms: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if GLOSSARY_PATH.exists():
            try:
                self._terms = json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))
            except Exception:
                self._terms = {}

    def save(self) -> None:
        GLOSSARY_PATH.write_text(
            json.dumps(self._terms, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @property
    def terms(self) -> dict[str, str]:
        return dict(self._terms)

    def set_terms(self, terms: dict[str, str]) -> None:
        self._terms = {k: v for k, v in terms.items() if k and v}

    def is_empty(self) -> bool:
        return not self._terms

    def apply(self, text: str) -> tuple[str, dict[str, str]]:
        """Replace source terms with unique placeholders. Returns (new_text, placeholder_map)."""
        result = text
        pm: dict[str, str] = {}
        for i, (src, tgt) in enumerate(self._terms.items()):
            if src in result:
                ph = f"\x00G{i}\x00"
                result = result.replace(src, ph)
                pm[ph] = tgt
        return result, pm

    def restore(self, text: str, pm: dict[str, str]) -> str:
        """Replace placeholders back with target translations."""
        result = text
        for ph, tgt in pm.items():
            result = result.replace(ph, tgt)
        return result
