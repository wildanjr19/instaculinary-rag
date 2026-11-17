import json
import logging
import re

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from openai import APITimeoutError
from pydantic import BaseModel, ConfigDict, Field, ValidationError, ValidationInfo, field_validator
import requests

from src.llm import load_llm
from src.normalization import normalize_account, normalize_instagram_url
from src.search import search_documents
from src.utils import build_context, build_prompt

logger = logging.getLogger(__name__)
app = FastAPI()

# Browser memakai proxy Next.js pada origin yang sama; backend tidak memerlukan CORS.

class QueryRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(min_length=1)


class CulinaryResult(BaseModel):
    rank: int
    name: str
    address: str
    hours: str
    price: str
    categories: list[str]
    description: str
    source: str
    source_url: str

    @field_validator("source")
    @classmethod
    def normalize_source(cls, value: str) -> str:
        return normalize_account(value) or "-"

    @field_validator("source_url")
    @classmethod
    def normalize_source_url(cls, value: str, info: ValidationInfo) -> str:
        return normalize_instagram_url(value, info.data.get("source", "")) or "-"


class RAGResponse(BaseModel):
    query_summary: str
    results: list[CulinaryResult]


@app.get("/") 
async def root():
    return {"status": "Backend Kuliner RAG Berjalan"}

@app.post("/api/chat", response_model=RAGResponse)
def chat(request: QueryRequest):
    # SDK sinkron dijalankan di thread pool FastAPI, bukan di ASGI event loop.
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
        response = load_llm().invoke(prompt)

        # --- 3. PARSE JSON (dengan toleransi markdown code block) ---
        raw = response.content.strip()
        
        # Hapus markdown code fence jika LLM bandel
        raw = re.sub(r'^```(?:json)?\s*', '', raw)
        raw = re.sub(r'\s*```$', '', raw)
        
        try:
            return RAGResponse.model_validate(json.loads(raw))
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
        except ValidationError:
            logger.warning("Respons LLM tidak sesuai format rekomendasi.")
            return JSONResponse(
                status_code=502,
                content={
                    "query_summary": "Jawaban layanan AI tidak dapat diproses.",
                    "results": [],
                    "error": "Format rekomendasi tidak valid. Silakan coba lagi.",
                },
            )

    except (requests.Timeout, APITimeoutError):
        logger.exception("Batas waktu layanan rekomendasi terlampaui.")
        return JSONResponse(
            status_code=504,
            content={
                "query_summary": "Layanan rekomendasi terlalu lama merespons.",
                "results": [],
                "error": "Batas waktu pencarian terlampaui. Silakan coba lagi.",
            },
        )
    except requests.RequestException:
        logger.exception("Layanan embedding gagal merespons.")
        return JSONResponse(
            status_code=502,
            content={
                "query_summary": "Layanan rekomendasi tidak tersedia.",
                "results": [],
                "error": "Layanan embedding sedang bermasalah. Silakan coba lagi.",
            },
        )
    except Exception:
        logger.exception("Pencarian rekomendasi kuliner gagal.")
        return JSONResponse(
            status_code=500,
            content={
                "query_summary": "Terjadi kesalahan sistem.",
                "results": [],
                "error": "Layanan rekomendasi sedang bermasalah. Silakan coba lagi.",
            },
        )
