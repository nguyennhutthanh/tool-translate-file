"""
translator_module.py
Translation engine using deep-translator (Google Translate backend).
Handles text chunking to stay within API character limits.
"""

from deep_translator import GoogleTranslator, MyMemoryTranslator

# Source language options (includes Auto-detect)
SOURCE_LANGUAGES = {
    "Auto-detect": "auto",
    "English":              "en",
    "Vietnamese":           "vi",
    "Japanese":             "ja",
    "Chinese (Simplified)": "zh-CN",
    "Korean":               "ko",
    "French":               "fr",
    "German":               "de",
    "Spanish":              "es",
    "Italian":              "it",
    "Portuguese":           "pt",
    "Russian":              "ru",
    "Arabic":               "ar",
    "Hindi":                "hi",
    "Thai":                 "th",
    "Indonesian":           "id",
}

# Target language options
LANGUAGES = {
    "English":              "en",
    "Vietnamese":           "vi",
    "Japanese":             "ja",
    "Chinese (Simplified)": "zh-CN",
    "Korean":               "ko",
    "French":               "fr",
    "German":               "de",
    "Spanish":              "es",
    "Italian":              "it",
    "Portuguese":           "pt",
    "Russian":              "ru",
    "Arabic":               "ar",
    "Hindi":                "hi",
    "Thai":                 "th",
    "Indonesian":           "id",
}

# Available translation providers
PROVIDERS = {
    "Google Translate (Free)": "google",
    "MyMemory (Free)":         "mymemory",
}

# MyMemory uses locale codes (e.g. "en-US") instead of plain codes
_MYMEMORY = {
    "auto": "en-US", "en": "en-US", "vi": "vi-VN", "ja": "ja-JP",
    "zh-CN": "zh-CN", "ko": "ko-KR", "fr": "fr-FR", "de": "de-DE",
    "es": "es-ES", "it": "it-IT", "pt": "pt-PT", "ru": "ru-RU",
    "ar": "ar-SA", "hi": "hi-IN", "th": "th-TH", "id": "id-ID",
}

# Google Translate API enforces a ~5 000-character limit per request
MAX_CHUNK_SIZE = 4_500


class TranslatorModule:
    """Translate text using Google Translate via deep-translator."""

    # ── Public API ────────────────────────────────────────────────────────────

    def translate_text(
        self,
        text: str,
        target_lang: str,
        source_lang: str = "auto",
        provider: str = "google",
        progress_callback=None,
    ) -> str:
        """Translate *text* into *target_lang* using the chosen *provider*."""
        if not text.strip():
            return ""

        chunks = self._split_into_chunks(text)

        if provider == "mymemory":
            src = _MYMEMORY.get(source_lang, source_lang)
            tgt = _MYMEMORY.get(target_lang, target_lang)
            translator = MyMemoryTranslator(source=src, target=tgt)
        else:
            translator = GoogleTranslator(source=source_lang, target=target_lang)

        translated_parts: list[str] = []
        for i, chunk in enumerate(chunks):
            if chunk.strip():
                result = translator.translate(chunk)
                translated_parts.append(result if result else chunk)
            else:
                translated_parts.append(chunk)
            if progress_callback:
                progress_callback(int((i + 1) / len(chunks) * 100))

        return "\n".join(translated_parts)

    def detect_language(self, text: str) -> str:
        """
        Attempt to detect the source language of *text*.
        Returns a BCP-47 language tag (e.g. 'en', 'vi') or 'unknown'.
        """
        try:
            from langdetect import detect  # optional dependency
            return detect(text[:800])
        except Exception:
            return "unknown"

    # ── Internals ─────────────────────────────────────────────────────────────

    def _split_into_chunks(self, text: str) -> list[str]:
        """
        Split *text* into paragraph-aligned chunks, each smaller than
        MAX_CHUNK_SIZE characters.  Paragraphs that are themselves too long
        are split at word boundaries (or character boundaries as a last resort).
        """
        paragraphs = text.split("\n")
        chunks: list[str] = []
        current: list[str] = []
        current_size = 0

        for para in paragraphs:
            # Paragraph itself exceeds limit — split it further
            if len(para) >= MAX_CHUNK_SIZE:
                if current:
                    chunks.append("\n".join(current))
                    current = []
                    current_size = 0
                # Split at word boundaries where possible
                words = para.split(" ")
                sub: list[str] = []
                sub_size = 0
                for word in words:
                    word_size = len(word) + 1  # +1 for the space
                    if sub_size + word_size >= MAX_CHUNK_SIZE and sub:
                        chunks.append(" ".join(sub))
                        sub = [word]
                        sub_size = word_size
                    else:
                        sub.append(word)
                        sub_size += word_size
                if sub:
                    chunks.append(" ".join(sub))
                continue

            para_size = len(para) + 1  # +1 accounts for the joining newline

            # If adding this paragraph would exceed the limit, flush first
            if current_size + para_size > MAX_CHUNK_SIZE and current:
                chunks.append("\n".join(current))
                current = [para]
                current_size = para_size
            else:
                current.append(para)
                current_size += para_size

        if current:
            chunks.append("\n".join(current))

        return chunks or [text]
