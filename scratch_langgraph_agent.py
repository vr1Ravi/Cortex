"""Scratch: the agent as a LangGraph state machine. Run once (rate limits!). Delete after."""

import asyncio

from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent

from app.core.config import settings
from app.core.database import async_session_maker
from app.repositories import document as document_repo
from app.services.retrieval import retrieve_chunks

OWNER_ID = 2

def build_agent(session, owner_id):
    # Same two tools — now as LangChain @tool functions (docstring = the description the model reads).

    @tool
    async def search_documents(query: str) -> str:
        """Search the user's documents for passages relevant to a query."""
        rows = await retrieve_chunks(session, query, owner_id, k=5)
        return "\n\n".join(
            f"[{c.document_id}:{c.chunk_index}] {c.content}" for c, _ in rows
        ) or "No relevant passages found."
    
    @tool
    async def list_documents() -> str:
         """List the titles of all the user's documents (which/how many exist)."""
         docs = await document_repo.list_all(session, owner_id, skip=0, limit=100)
         return "\n".join(f"[{d.id}] {d.title}" for d in docs) or "No documents."
    
    llm = ChatGoogleGenerativeAI(model=settings.gemini_model, google_api_key=settings.google_api_key)
    # This ONE call builds the whole graph: agent node, tools node, conditional edge, loop.
    return create_react_agent(llm, tools=[search_documents, list_documents])


async def main():
    async with async_session_maker() as session:
        agent = build_agent(session, OWNER_ID)
        result = await agent.ainvoke(
            {
                "messages": [("user", "What is the first project mentioned in my resume?")]
            }
        )

        for m in result["messages"]:  # see EVERY step: user → tool call → tool result → answer
            m.pretty_print()

asyncio.run(main())