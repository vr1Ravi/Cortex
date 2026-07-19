"""Document analysis via Gemini structured output."""

from google.genai import types

from app.core.llm import generate
from app.schemas.analysis import DocumentAnalysis


async def analyze_document(content: str) -> DocumentAnalysis:
    response = await generate(
        contents=f"Analyze the following document:\n\n{content}",
        config=types.GenerateContentConfig(
            system_instruction=(
                "You are a document analyst. Produce a short summary, a list of "
                "relevant topical tags, and the key points."
            ),
            response_mime_type="application/json", # force JSON output
            response_schema=DocumentAnalysis      # ...matching THIS schema
        )
    )
    return response.parsed                        # already a validated DocumentAnalysis instance