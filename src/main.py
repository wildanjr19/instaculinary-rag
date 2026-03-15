"""
Via terminal
"""

import os

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


def main():
    query = input("Masukkan pertanyaan kuliner Anda: ")

    # retrieve documents (local vector DB)
    docs = search_documents(query, k=5)

    if not docs:
        print("Maaf, informasi tidak ditemukan.")
        return

    # build context & prompt
    context = build_context(docs)
    prompt = build_prompt(context, query)

    # load DeepSeek
    llm = load_llm()

    # generate answer
    response = llm.invoke(prompt)

    print("\nJawaban:\n")
    print(response.content)


if __name__ == "__main__":
    main()
