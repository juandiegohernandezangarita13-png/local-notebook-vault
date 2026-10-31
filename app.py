import streamlit as st

from src.indexer import index_vault
from src.rag_engine import query_notes, list_ollama_models

st.set_page_config(page_title="Local Vault Notebook", layout="wide")

st.sidebar.title("Configuración")

vault_path = st.sidebar.text_input("Ruta de notas (.md):", value="./data/vault")

available_models = list_ollama_models()
if not available_models:
    st.sidebar.error(
        "No encuentro modelos de Ollama. Comprueba que Ollama está en ejecución "
        "y descarga uno, por ejemplo: ollama pull llama3"
    )
    available_models = ["llama3:latest"]
selected_model = st.sidebar.selectbox("Modelo Ollama:", available_models)

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
        if msg.get("sources"):
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
        "sources": result["sources"],
    })
