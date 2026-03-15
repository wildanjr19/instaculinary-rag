import gradio as gr
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Tambah root project ke sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.search import search_documents
from src.utils import build_context, build_prompt
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.environ["DEEPSEEK_API_KEY"],
    temperature=0.3
)

def rag_chat(query):
    docs = search_documents(query, k=5)
    if not docs:
        return "Maaf, informasi tidak ditemukan."

    context = build_context(docs)
    prompt = build_prompt(context, query)
    response = llm.invoke(prompt)

    return response.content

gr.Interface(
    fn=rag_chat,
    inputs=gr.Textbox(label="Pertanyaan Kuliner"),
    outputs=gr.Textbox(label="Jawaban"),
    title="Kitab Kuliner Yogyakarta"
).launch()
