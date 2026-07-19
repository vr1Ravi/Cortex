"""Grounded question-answering over a document."""

from google.genai import types

from app.core.llm import generate

QA_SYSTEM_INSTRUCTION = (
    "You are Cortex, a document assistant. Answer the user's question using ONLY the "
    "provided document. If the answer isn't in the document, say you can't find it in the "
    "document. Do not use outside knowledge."
)


async def answer_from_document(question: str, document: str) -> str:
    prompt = f'Document:\n"""\n{document}\n"""\n\nQuestion: {question}'
    response = await generate(
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=QA_SYSTEM_INSTRUCTION)
    )
    return response.text