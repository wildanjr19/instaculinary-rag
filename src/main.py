"""
CLI untuk menjalankan RAG via terminal.
Output sekarang dalam format JSON terstruktur.
"""

import json
import os
import re

from dotenv import load_dotenv
load_dotenv()  # load .env

from src.search import search_documents
from src.utils import build_context, build_prompt

from langchain_openai import ChatOpenAI


def load_llm():
    return ChatOpenAI(
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key=os.environ["DEEPSEEK_API_KEY"],
        temperature=0.3
    )


def parse_json_response(raw: str) -> dict:
    """Parse respons LLM ke JSON, toleransi markdown code block."""
    raw = raw.strip()
    raw = re.sub(r'^```(?:json)?\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    return json.loads(raw)


def main():
    query = input("Masukkan pertanyaan kuliner Anda: ")

    docs = search_documents(query, k=5)

    if not docs:
        print(json.dumps({
            "query_summary": "Tidak ada data relevan ditemukan.",
            "results": []
        }, ensure_ascii=False, indent=2))
        return

    context = build_context(docs)
    prompt = build_prompt(context, query)

    llm = load_llm()
    response = llm.invoke(prompt)

    try:
        result = parse_json_response(response.content)
        print("\n" + json.dumps(result, ensure_ascii=False, indent=2))
    except json.JSONDecodeError:
        print("\n⚠️ LLM tidak mengembalikan JSON valid. Output mentah:")
        print(response.content)


if __name__ == "__main__":
    main()
