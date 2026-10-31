import streamlit as st
import os
from src.indexer import index_vault
from src.rag_engine import query_notes

st.set_page_config(page_title="Local Vault Notebook", layout="wide")

st.sidebar.title("Configuración")
vault_path = st.sidebar.text_input("Ruta de notas (.md):", value="./data/vault")
selected_model = st.sidebar.selectbox("Modelo Ollama:", ["llama3:latest", "mistral:latest", "qwen2.5:latest"])

if st.sidebar.button("Reindexar Notas"):
    with st.spinner("Indexando notas locales en ChromaDB..."):
        total_chunks, total_files = index_vault(vault_dir=vault_path)
        st.sidebar.success(f"{total_files} archivos ({total_chunks} fragmentos) indexados.")

st.title("🧠 Local Notebook Vault")
st.caption("Pregunta directamente sobre tu archivo de notas Markdown locales de forma 100% privada.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
        if "sources" in msg and msg["sources"]:
            st.caption(f"Fuentes: {', '.join(msg['sources'])}")

if prompt := st.chat_input("Haz una pregunta sobre tus notas..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Buscando en tus notas y generando respuesta..."):
            result = query_notes(question=prompt, model=selected_model)
            st.write(result["answer"])
            if result["sources"]:
                st.caption(f"Fuentes: {', '.join(result['sources'])}")
            
            st.session_state.messages.append({
                "role": "assistant",
                "content": result["answer"],
                "sources": result["sources"]
            })
