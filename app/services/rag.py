"""The RAG pipeline: retrieve relevant chunks → augment the prompt → generate a grounded answer."""


from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import generate
from app.models.chunk import DocumentChunk
from app.services.retrieval import retrieve_chunks

RAG_SYSTEM_INSTRUCTION = (
    "You are Cortex, a document assistant. Answer the question using ONLY the provided context. "
    "Cite the sources you use inline as [source document_id:chunk_index]. If the context does not "
    "contain the answer, say you couldn't find it in the documents. Do not use outside knowledge."
)
MAX_DISTANCE = 0.45   # relevance floor — tune per your data (see caveat below)


async def answer_with_rag(
        session: AsyncSession, question: str, owner_id: int, k: int = 5
) -> tuple[str, list[DocumentChunk]]:
    #1. RETRIEVE
    rows = await retrieve_chunks(session, question, owner_id, k)
    # Keep only chunks actually close enough to be relevant.
    relevant = [(c, dist) for c, dist in rows if dist <= MAX_DISTANCE]
    if not relevant:
        return "I couldn't find anything relevant in your documents.", []   # ← no citations, no LLM call
    
    chunks = [chunk for chunk, _distance in relevant]
    if not chunks:
        return "I couldn't find anything relevant in your documents.", []
    
    #2. AGUMENT - stuff only the retrieved chunks, each labelled with its source
    context = "\n\n".join(
        f"[source {c.document_id}:{c.chunk_index}]\n{c.content}" for c in chunks
    )
    prompt = f"Context:\n{context}\n\nQuestion: {question}"

    #3. GENERATE
    response = await generate(
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=RAG_SYSTEM_INSTRUCTION),
    )
    return response.text, chunks
