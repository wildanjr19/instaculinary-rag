from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys
import time
from dotenv import load_dotenv

# Monitoring Libraries
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram

# root path untuk import src prevent eror
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from src.search import search_documents
from src.utils import build_context, build_prompt
from langchain_openai import ChatOpenAI

app = FastAPI()

# --- DEFINISI METRIK CUSTOM ---
# 1. Menghitung total pertanyaan yang masuk
TOTAL_CHAT_REQUESTS = Counter("rag_chat_requests_total", "Total request ke API Chat")

# 2. Latency Vector DB (Pinecone/Chroma/dll)
VECTOR_DB_LATENCY = Histogram(
    "rag_vector_db_latency_seconds", 
    "Waktu pencarian dokumen di Vector DB",
    buckets=(.05, .1, .25, .5, 1.0, 2.5, 5.0)
)

# 3. Latency DeepSeek LLM
LLM_GENERATE_LATENCY = Histogram(
    "rag_llm_latency_seconds", 
    "Waktu respon dari DeepSeek API",
    buckets=(.5, 1.0, 2.0, 5.0, 10.0, 20.0, 60.0)
)

# 4. Counter Error (Jika API DeepSeek down atau Vector DB timeout)
RAG_ERRORS = Counter("rag_errors_total", "Total error pada sistem RAG", ["type"])

# --- INISIALISASI INSTRUMENTATOR ---
# Ini untuk metrik standar (HTTP req, Memory, CPU)
instrumentator = Instrumentator().instrument(app)

@app.on_event("startup")
async def startup():
    # Ekspos metrik di path /metrics
    instrumentator.expose(app, endpoint="/metrics")

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
    TOTAL_CHAT_REQUESTS.inc()
    
    try:
        # --- 1. SEARCHING (Vector DB Metric) ---
        start_vec = time.time()
        docs = search_documents(request.query, k=5)
        VECTOR_DB_LATENCY.observe(time.time() - start_vec)

        if not docs:
            return {"answer": "Maaf, informasi tidak ditemukan."}
        
        context = build_context(docs)
        prompt = build_prompt(context, request.query)

        # --- 2. GENERATING (LLM Metric) ---
        start_llm = time.time()
        response = llm.invoke(prompt)
        LLM_GENERATE_LATENCY.observe(time.time() - start_llm)

        return {"answer": response.content}

    except Exception as e:
        # Mencatat tipe error (misal: DeepSeek API Error atau Connection Error)
        error_type = type(e).__name__
        RAG_ERRORS.labels(type=error_type).inc()
        return {"error": "Terjadi kesalahan pada sistem.", "details": str(e)}