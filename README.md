# Local Notebook Vault

Aplicación local que combina notas Markdown con un motor RAG privado: pregunta sobre tus notas sin internet ni APIs de terceros.

## Requisitos
- Python 3.10+
- [Ollama](https://ollama.com/) instalado y en ejecución

## Instalación
git clone https://github.com/juandiegohernandezangarita13-png/local-notebook-vault.git
cd local-notebook-vault
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
ollama pull llama3

## Uso
streamlit run app.py

1. Indica la ruta de tus notas .md en la barra lateral (por defecto ./data/vault).
2. Pulsa "Reindexar Notas".
3. Pregunta en el chat; cada respuesta cita sus fuentes.

## Estructura
- app.py: interfaz Streamlit
- src/indexer.py: indexado de notas en ChromaDB
- src/rag_engine.py: búsqueda y generación con Ollama
- data/vault/: notas de ejemplo
