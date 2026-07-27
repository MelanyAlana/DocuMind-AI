"""Interfaz de DocuMind AI."""
from __future__ import annotations

import time

import streamlit as st

from src.chatbot import answer_question
from src.config import APP_TITLE, ensure_directories, has_api_key
from src.rag import index_uploaded_pdf


st.set_page_config(page_title=APP_TITLE, page_icon="📄", layout="wide")
ensure_directories()

st.markdown(
    """<style>
    .stApp {background: #0b1020; color: #e7eaf0;}
    [data-testid="stSidebar"] {background: #111936;}
    .hero {padding: .8rem 0 1.2rem;} .hero h1 {margin-bottom: .2rem;}
    .source {border-left: 3px solid #7c9cff; padding-left: 12px; margin: 8px 0; color: #cbd5e1;}
    </style>""",
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []
if "index" not in st.session_state:
    st.session_state.index = None
if "stats" not in st.session_state:
    st.session_state.stats = None

with st.sidebar:
    st.header("⚙️ Configuración")
    top_k = st.slider("Fragmentos a consultar", 2, 8, 4)
    model = st.selectbox("Modelo", ["command-a-plus-05-2026", "command-a-03-2025"], index=0)
    st.divider()
    if st.button("🗑️ Limpiar conversación", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    if st.session_state.stats:
        st.divider()
        st.caption("DOCUMENTO ACTIVO")
        st.write(f"**{st.session_state.stats['file_name']}**")
        st.caption(f"{st.session_state.stats['pages']} páginas · {st.session_state.stats['chunks']} fragmentos")

st.markdown("<div class='hero'><h1>📄 DocuMind AI</h1><p>Consulta tus documentos con respuestas fundamentadas en su contenido.</p></div>", unsafe_allow_html=True)

if not has_api_key():
    st.warning("Configura `COHERE_API_KEY` en el archivo `.env` antes de procesar documentos.")

uploaded = st.file_uploader("Sube un documento PDF", type=["pdf"], help="El PDF se procesa localmente y solo se envían fragmentos a Cohere para crear embeddings y responder.")
if uploaded and (not st.session_state.stats or st.session_state.stats["file_name"] != uploaded.name):
    if has_api_key():
        try:
            with st.spinner("Leyendo, fragmentando e indexando el documento..."):
                started = time.perf_counter()
                index, stats = index_uploaded_pdf(uploaded.name, uploaded.getvalue())
                stats["seconds"] = round(time.perf_counter() - started, 1)
                st.session_state.index = index
                st.session_state.stats = stats
                st.session_state.messages = []
            st.success(f"Documento listo en {stats['seconds']} s.")
        except Exception as exc:
            st.error(f"No se pudo procesar el PDF: {exc}")

if st.session_state.stats:
    a, b, c = st.columns(3)
    a.metric("Páginas", st.session_state.stats["pages"])
    b.metric("Fragmentos", st.session_state.stats["chunks"])
    c.metric("Tiempo", f"{st.session_state.stats['seconds']} s")

st.divider()
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for source in message.get("sources", []):
            st.markdown(f"<div class='source'><b>Página {source['page']}</b><br>{source['text']}</div>", unsafe_allow_html=True)

question = st.chat_input("Pregunta algo sobre el documento…", disabled=st.session_state.index is None)
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Buscando en el documento..."):
            try:
                result = answer_question(st.session_state.index, question, top_k=top_k, model=model)
                st.markdown(result["answer"])
                with st.expander("Ver fuentes utilizadas"):
                    for source in result["sources"]:
                        st.markdown(f"**Página {source['page']}**  ")
                        st.caption(source["text"])
                st.session_state.messages.append({"role": "assistant", "content": result["answer"], "sources": result["sources"]})
            except Exception as exc:
                st.error(f"No se pudo generar la respuesta: {exc}")
