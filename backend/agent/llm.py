"""
Shared Groq LLM client. Centralized so every node uses the same model and
config, and so swapping the model later is a one-line change.
"""
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)