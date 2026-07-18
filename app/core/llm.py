"""Google Gemini async client."""

from google import genai

from app.core.config import settings

gemini = genai.Client(api_key=settings.google_api_key)
# gemini.aio.* are the ASYNC methods (won't block the event loop — Phase 0).