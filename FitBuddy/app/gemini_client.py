import logging
import os
import time

from google import genai
from google.genai import errors, types

logger = logging.getLogger("fitbuddy.gemini")

MAX_ATTEMPTS = 3
RETRYABLE_CODES = {429, 500, 502, 503, 504}
_client = None


class GeminiError(Exception):
    """Raised when Gemini is misconfigured, unavailable, or returns no usable text."""


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise GeminiError("GOOGLE_API_KEY is not configured.")
        _client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=60_000))
    return _client


def generate_text(model: str, prompt: str, temperature: float) -> str:
    """Call Gemini with retry and exponential backoff on transient errors."""
    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = _get_client().models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(temperature=temperature),
            )
        except errors.APIError as exc:
            last_error = exc
            logger.warning("Gemini call failed (attempt %s, code %s): %s", attempt, exc.code, exc)
            if exc.code not in RETRYABLE_CODES or attempt == MAX_ATTEMPTS:
                break
            time.sleep(2 ** (attempt - 1))
            continue
        text = (response.text or "").strip()
        if not text:
            raise GeminiError("Gemini returned an empty response (possibly blocked by safety filters).")
        return text
    raise GeminiError("Gemini request failed.") from last_error
