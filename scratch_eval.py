"""Scratch: measure RAG retrieval quality. `python scratch_eval.py`. Delete after."""

import asyncio

from google.genai import types
from pydantic import BaseModel, Field

from app.core.llm import generate
from app.services.rag import answer_with_rag

from app.core.database import async_session_maker
from app.services.retrieval import retrieve_chunks

class Judgment(BaseModel):
    faithful: bool = Field(description="True only if EVERY claim in the answer is supported by the context")
    relevant: bool = Field(description="True if the answer actually addresses the question")
    reason: str = Field(description="One-sentence justification")

JUDGE_PROMPT = """You are a strict RAG grader. Judge the ANSWER against the CONTEXT and QUESTION.
- faithful: is every claim in the answer supported by the context? (No outside knowledge allowed.)
- relevant: does the answer address the question?

QUESTION: {question}

CONTEXT:
{context}

ANSWER: {answer}"""


OWNER_ID = 2   # your user id (from the SQL logs)
K = 5

# Your labeled eval set: question → the document_id that SHOULD answer it.
# Write 5–8 questions across DIFFERENT docs so the metric isn't trivially 100%.
# Include at least one OFF-TOPIC question with expected_doc=None (should retrieve nothing relevant).
EVAL = [
    {"question": "What is the first project mentioned in the resume?", "expected_doc": 4},
    {"question": "What is Global?", "expected_doc": 4},
    {"question": "What is the capital of France?",                      "expected_doc": None},  # off-topic
]

MAX_DISTANCE = 0.45   # same floor as your RAG


async def judge(question: str, context: str, answer: str) -> Judgment:
    resp = await generate(
        contents=JUDGE_PROMPT.format(question=question, context=context, answer=answer),
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=Judgment,   # ← forces structured output (4.3 pattern)
        ),
    )
    return resp.parsed

async def eval_generation():
    async with async_session_maker() as session:
        faithful = relevant = total = 0
        for ex in EVAL:
            if ex["expected_doc"] is None:      # skip off-topic; nothing to generate from
                continue
            answer, chunks = await answer_with_rag(session, ex["question"], OWNER_ID, K)
            context = "\n\n".join(c.content for c in chunks)
            j = await judge(ex["question"], context, answer)
            total += 1
            faithful += j.faithful
            relevant += j.relevant
            mark = "✅" if (j.faithful and j.relevant) else "⚠️"
            print(f"{mark} {ex['question'][:45]:45} faithful={j.faithful} relevant={j.relevant} — {j.reason}")
        print(f"\nFaithfulness: {faithful}/{total}   Answer-relevance: {relevant}/{total}")


async def main():
    async with async_session_maker() as session:
        hits = 0
        for ex in EVAL:
            rows = await retrieve_chunks(session, ex["question"], OWNER_ID, K)
            # apply the floor, like real RAG does
            relevant = [(c, d) for c, d in rows if d <= MAX_DISTANCE]
            retrieved_docs = {c.document_id for c, _ in relevant}

            if ex["expected_doc"] is None:                 # off-topic → success = retrieved nothing
                hit = len(relevant) == 0
            else:
                hit = ex["expected_doc"] in retrieved_docs

            hits += hit
            print(f"{'✅' if hit else '❌'} {ex['question'][:50]:50}  → docs {retrieved_docs or '∅'}")

        print(f"\nHit-rate@{K}: {hits}/{len(EVAL)} = {hits / len(EVAL):.0%}")


asyncio.run(eval_generation())
