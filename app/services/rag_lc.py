"""RAG rebuilt as a LangChain LCEL chain — compare side-by-side with services/rag.py."""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableBranch,
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
)
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.services.retrieval import retrieve_chunks

RAG_PROMPT = ChatPromptTemplate.from_template(
    "Answer the question using ONLY the context below. "
    "If the answer isn't in the context, say you don't know. \n\n"
    "Cite each fact as [source doc:chunk] using the labels in the context.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}"
)
MAX_DISTANCE = 0.45   # same floor as your hand-built answer_with_rag
NOT_FOUND = "I couldn't find anything relevant in your documents."

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.google_api_key
)

def _format_docs(rows) -> str:
    """rows = list of (DocumentChunk, distance) from retrieve_chunks → one context string."""
    return "\n\n".join(
        f"[source {c.document_id}:{c.chunk_index}]\n{c.content}" for c, _ in rows
    )
async def answer_with_rag_lc(
        session: AsyncSession,
        question: str,
        owner_id: int,
        k: int = 5
) -> tuple[str, list]:
    # A closure binds session + owner_id (which aren't part of the chain's "question" input).
    async def retrieve(q: str):
        rows = await retrieve_chunks(session, q, owner_id, k)   # returns rows now, not a string
        return [(c, dist) for c, dist in rows if dist <= MAX_DISTANCE]
    
    # LCEL's if/else: if no rows survived the floor → canned message (NO llm call); else generate.
    answer_step = RunnableBranch(
        (lambda x: not x["rows"], lambda x: NOT_FOUND),  # (condition, what-to-run-if-true)
        RAG_PROMPT | llm | StrOutputParser()
    )
    
    # Step 1: run retrieval once, carry the question alongside the rows.
    setup = RunnableParallel(rows=RunnableLambda(retrieve), question=RunnablePassthrough())

    # Step 2: build the answer from those rows, but keep the rows too.
    answer_chain = (
        RunnablePassthrough.assign(context=lambda x: _format_docs(x["rows"]))
        | RunnablePassthrough.assign(
            answer=answer_step
        )
    )
    chain = setup | answer_chain
    result = await chain.ainvoke(question)   
    # → {"rows": [...], "question": ..., "context": ..., "answer": ...}
    return result["answer"], result["rows"]  # now the endpoint can build citations!