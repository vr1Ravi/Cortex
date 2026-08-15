"""Scratch: watch the agent loop. `python scratch_agent.py`. Delete after."""

import asyncio

from app.core.database import async_session_maker
from app.services.agent import run_agent

OWNER_ID = 2


async def ask(question: str):
    async with async_session_maker() as session:
        print(f"\n❓ {question}")
        answer = await run_agent(session, question, OWNER_ID)
        print(f"💬 {answer}")


async def main():
    # await ask("What is the first project mentioned in my resume?")  # should CALL the tool
    # await ask("What is 17 * 23?")                                   # should NOT — pure reasoning
    await ask("How many documents do I have, and what are they?")   # should call list_documents



asyncio.run(main())
