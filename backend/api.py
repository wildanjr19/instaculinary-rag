from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
import re
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

# DeepSeek setup
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
    try:
        # --- 1. SEARCHING ---
        docs = search_documents(request.query, k=5)

        if not docs:
            return {
                "query_summary": "Tidak ada data relevan ditemukan.",
                "results": []
            }
        
        context = build_context(docs)
        prompt = build_prompt(context, request.query)

        # --- 2. GENERATING ---
        response = llm.invoke(prompt)

        # --- 3. PARSE JSON (dengan toleransi markdown code block) ---
        raw = response.content.strip()
        
        # Hapus markdown code fence jika LLM bandel
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        
        try:
            result = json.loads(raw)
            return result
        except json.JSONDecodeError:
            # Fallback: bungkus teks mentah sebagai deskripsi
            return {
                "query_summary": f"Pencarian: {request.query}",
                "results": [{
                    "rank": 1,
                    "name": "Hasil Pencarian",
                    "address": "-",
                    "hours": "-",
                    "price": "-",
                    "categories": [],
                    "description": raw,
                    "source": "-",
                    "source_url": "-"
                }]
            }

    except Exception as e:
        return {
            "query_summary": "Terjadi kesalahan sistem.",
            "results": [],
            "error": str(e)
        }

    except Exception as e:
        # Mencatat tipe error (misal: DeepSeek API Error atau Connection Error)
        error_type = type(e).__name__
        RAG_ERRORS.labels(type=error_type).inc()
        return {"error": "Terjadi kesalahan pada sistem.", "details": str(e)}