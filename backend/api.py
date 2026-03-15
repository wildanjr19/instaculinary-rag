from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
from dotenv import load_dotenv

# Tambahkan ini agar VPS bisa menemukan folder src kamu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from src.search import search_documents
from src.utils import build_context, build_prompt
from langchain_openai import ChatOpenAI

app = FastAPI()

# PERBAIKAN CORS: Izinkan domain kamu agar frontend bisa akses
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Sementara set ke "*" agar pasti jalan, atau masukkan domain kamu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pastikan DEEPSEEK_API_KEY sudah ada di file .env di VPS!
llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    temperature=0.3
)

class QueryRequest(BaseModel):
    query: str

@app.get("/") # Tambahkan ini untuk tes di browser
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