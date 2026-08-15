"""A minimal agent: an LLM in a loop that can call tools over the user's documents."""

from google.genai import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm import generate
from app.services.retrieval import retrieve_chunks
from app.repositories import document as document_repo

# 1. DESCRIBE the tool to the model — name, what it does, and its parameter schema.
#    The model reads THIS to decide when/how to call it. Good descriptions = good agents.

search_documents_decl = types.FunctionDeclaration(
    name="search_documents",
    description=(
        "Search the user's own documents for passages relevant to a query. "
        "Use this whenever the question might be answered by the user's documents."
    ),
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string", "description": "A focused natural-language search query."
            },
        },
        "required": ["query"]
    }
)

list_documents_decl = types.FunctionDeclaration(
    name="list_documents",
    description=(
        "List the titles of all the user's documents. Use this for questions about WHICH "
        "documents exist or HOW MANY there are — not for searching their content."
    ),
    parameters={"type": "object", "properties": {}},   # no arguments
)

TOOLS = types.Tool(function_declarations=[search_documents_decl, list_documents_decl])

AGENT_SYSTEM = (
    "You are Cortex, an assistant over the user's documents. "
    "When a question may be answered by their documents, call search_documents "
    "(you may call it multiple times with different queries). "
    "Answer ONLY from what the tool returns; if nothing relevant is found, say so. "
    "Cite sources as [doc:chunk]."

)

MAX_STEPS = 5   # safety cap — never let an agent loop forever

async def run_agent(session: AsyncSession, question: str, owner_id: int) -> str:
    # The running conversation. It GROWS each loop: question → tool call → tool result → ...
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]
    config = types.GenerateContentConfig(tools=[TOOLS], system_instruction=AGENT_SYSTEM)

    for step in range(MAX_STEPS):
        response = await generate(contents=contents, config=config)
        calls = response.function_calls  # list of requested tool calls, or None

        if not calls:                      # (a) no tool wanted → FINAL answer → done
            return response.text
        
         # (b) the model requested tool(s). First record its turn (role="model")...
        contents.append(response.candidates[0].content)

        # ...then WE execute each requested tool and collect the results.
        tool_parts = []
        for call in calls:
            print(f"🛠️  step {step}: agent calls {call.name}({dict(call.args)})")   # watch it think
            if call.name == "search_documents":
                rows = await retrieve_chunks(session, call.args["query"], owner_id, k=5)
                result = "\n\n".join(
                    f"[{c.document_id}:{c.chunk_index}] {c.content}" for c, _ in rows
                ) or "No relevant passages found."
            elif call.name == "list_documents":
                docs = await document_repo.list_all(session, owner_id, skip=0, limit=100)
                result = "\n".join(f"[{d.id}] {d.title}" for d in docs) or "No documents."
            else:
                result = f"Unknown tool: {call.name}"
            
            tool_parts.append(
                types.Part.from_function_response(name=call.name, response={"result": result})
            )
        
        # Feed the tool results back into the conversation (role="user", as Gemini expects).
        contents.append(types.Content(role="user", parts=tool_parts))
    
    return "I couldn't finish within the step limit."
