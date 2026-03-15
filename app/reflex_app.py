import reflex as rx
import os
import sys
from dotenv import load_dotenv

# Load env dan path agar bisa baca folder src
load_dotenv()
sys.path.append(os.getcwd())

from src.search import search_documents
from src.utils import build_context, build_prompt
from langchain_openai import ChatOpenAI

# Inisialisasi LLM
llm = ChatOpenAI(
    model="deepseek-chat",
    base_url="https://api.deepseek.com",
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    temperature=0.3
)

class State(rx.State):
    """Logika backend aplikasi."""
    query: str = ""
    answer: str = ""
    is_loading: bool = False

    def get_answer(self):
        """Fungsi RAG yang dipindahkan dari rag_chat Gradio."""
        if not self.query.strip():
            return

        self.is_loading = True
        yield # Trigger UI untuk munculkan loading spinner

        try:
            # 1. Search lokal (ChromaDB)
            docs = search_documents(self.query, k=5)
            
            if not docs:
                self.answer = "Maaf, informasi tidak ditemukan di Kitab Kuliner."
            else:
                # 2. Build context & prompt
                context = build_context(docs)
                prompt = build_prompt(context, self.query)
                
                # 3. Invoke LLM via API
                response = llm.invoke(prompt)
                self.answer = response.content
        except Exception as e:
            self.answer = f"Terjadi kesalahan: {str(e)}"
        finally:
            self.is_loading = False

def index() -> rx.Component:
    """Tampilan Frontend."""
    return rx.center(
        rx.vstack(
            rx.heading("🍱 Kitab Kuliner Yogyakarta", size="8", color_scheme="orange"),
            rx.text("Tanya apa saja seputar kuliner khas Jogja dari data Instagram"),
            
            rx.input(
                placeholder="Misal: Gudeg yang buka sampai malam di mana?",
                on_change=State.set_query,
                on_enter=State.get_answer,
                width="100%",
                size="3",
            ),
            
            rx.button(
                "Cari Jawaban",
                on_click=State.get_answer,
                loading=State.is_loading,
                width="100%",
                color_scheme="orange",
                cursor="pointer",
            ),
            
            rx.divider(),
            
            # Area Jawaban
            rx.cond(
                State.answer != "",
                rx.card(
                    rx.text(State.answer, white_space="pre-wrap"),
                    header=rx.heading("Hasil Penelusuran", size="4"),
                    width="100%",
                    variant="ghost",
                ),
            ),
            
            spacing="5",
            padding="2em",
            max_width="600px",
            width="100%",
            box_shadow="lg",
            border_radius="xl",
            margin_y="4em",
        ),
        width="100%",
    )

app = rx.App(
    theme=rx.theme(accent_color="orange", radius="large")
)
app.add_page(index, title="Kitab Kuliner Yogyakarta")