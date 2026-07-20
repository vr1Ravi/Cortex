"""Turn text into embedding vectors via Gemini."""

from google.genai import types

from app.core.config import settings
from app.core.llm import gemini


async def embed_texts(texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
    """Embed a batch of texts → list of 768-dim vectors."""
    result = await gemini.aio.models.embed_content(
        model=settings.embedding_model,
        contents=texts,
        config=types.EmbedContentConfig(
            output_dimensionality=settings.embedding_dim,
            task_type=task_type
        )
    )
    return [e.values for e in result.embeddings]