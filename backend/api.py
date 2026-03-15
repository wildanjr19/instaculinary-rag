from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from dotenv import load_dotenv

# root path untuk import src prevent eror
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from src.search import search_documents
from src.utils import build_context, build_prompt
from langchain_openai import ChatOpenAI

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DeepSeek
llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.3
)

class QueryRequest(BaseModel):
    query: str

@app.get("/") 
async def root():
    return {"status": "Backend Kuliner RAG Berjalan"}

@app.post("/api/chat")
async def chat(request: QueryRequest):
    docs = search_documents(request.query, k=5)
    if not docs:
        return {"answer": "Maaf, informasi tidak ditemukan."}
    
    context = build_context(docs)
    prompt = build_prompt(context, request.query)
    response = llm.invoke(prompt)
    return {"answer": response.content}