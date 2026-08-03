"""Scratch: feel LCEL. Run with `python scratch_langchain.py`. Delete after."""


from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import settings

#1. Each peice is a Runnable:
prompt = ChatPromptTemplate.from_template(
    "Explain {topic} to a backend engineer in exactly 2 sentences."
)

llm = ChatGoogleGenerativeAI(
    model=settings.gemini_model,
    google_api_key=settings.google_api_key
)
 
parser = StrOutputParser()   # pulls the plain .content string out of the LLM's message object

#2. Compose them with | into one Runnable:
chain = prompt | llm | parser

#3. Drive it. .invoke() takes the prompt's input variables as a dict:
print(chain.invoke({"topic": "connection pooling"}))

print("\n--- streaming ---")
for piece in chain.stream({"topic": "backpressure"}): # streaming for FREE — same chain
    print(piece, end="", flush=True)
print()