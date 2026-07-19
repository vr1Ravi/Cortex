"""Google Gemini async client + a robust generate() wrapper."""

import asyncio
import logging

from google import genai
from google.genai import errors as genai_errors

from app.core.config import settings
from app.core.exceptions import LLMError

logger = logging.getLogger("cortex.llm")

gemini = genai.Client(api_key=settings.google_api_key)
# gemini.aio.* are the ASYNC methods (won't block the event loop — Phase 0).

MAX_RETRIES = 3
TIMEOUT_SECONDS = 30
TRANSIENT_CODES = {429, 500, 503}

async def generate(**kwargs):
    """Robust Gemini call: timeout + retry transient errors w/ backoff + usage log + clean LLMError.

    Pass any generate_content kwargs (contents=, config=). Model defaults from settings.
    """
    last_exc: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            async with asyncio.timeout(TIMEOUT_SECONDS):
                response = await gemini.aio.models.generate_content(
                    model=settings.gemini_model, **kwargs
                )
            u = response.usage_metadata
            logger.info(
                "Gemini tokens — prompt=%s output=%s total=%s",
                u.prompt_token_count, u.candidates_token_count, u.total_token_count,
            )
            return response
        except genai_errors.APIError as e:
            last_exc = e
            if e.code not in TRANSIENT_CODES:
                break
            wait = 2 ** attempt
            logger.warning(
                "Gemini %s (attempt %s/%s), retrying in %ss",
                e.code, attempt + 1, 
                MAX_RETRIES, 
                wait
                )
            await asyncio.sleep(wait)
        except TimeoutError as e:
            last_exc = e
            logger.warning("Gemini timed out (attempt %s/%s)", attempt + 1, MAX_RETRIES)
    raise LLMError("Gemini call failed after retries") from last_exc