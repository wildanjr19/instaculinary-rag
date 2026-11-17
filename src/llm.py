"""Konfigurasi DeepSeek yang dipakai backend dan CLI."""
from functools import lru_cache

from langchain_openai import ChatOpenAI

from config.config import get_required_env


@lru_cache(maxsize=1)
def load_llm():
    return ChatOpenAI(
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key=get_required_env("DEEPSEEK_API_KEY"),
        temperature=0.3,
        timeout=45,
        max_retries=0,  # Hindari retry tersembunyi yang menggandakan waktu generasi.
    )
