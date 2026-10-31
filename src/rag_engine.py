import ollama
from src.indexer import get_chroma_collection

def query_notes(question: str, top_k: int = 4, model: str = "llama3:latest") -> dict:
    collection = get_chroma_collection()
    
    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )
    
    retrieved_docs = results.get("documents", [[]])[0]
    retrieved_meta = results.get("metadatas", [[]])[0]
    
    if not retrieved_docs:
        context = "No se encontraron notas relevantes en la base local."
        sources = []
    else:
        context_parts = []
        sources = []
        for doc, meta in zip(retrieved_docs, retrieved_meta):
            source_name = meta.get("source", "desconocido")
            sources.append(source_name)
            context_parts.append(f"--- Documento: {source_name} ---\n{doc}")
        context = "\n\n".join(context_parts)
    
    system_prompt = (
        "Eres un asistente de notas locales. "
        "Responde a la pregunta del usuario utilizando de forma estricta el contexto de las notas proporcionadas. "
        "Si la respuesta no se encuentra en las notas, dilo explícitamente y no inventes."
    )
    
    user_prompt = f"Contexto extraído de mis notas:\n{context}\n\nPregunta: {question}"
    
    response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return {
        "answer": response["message"]["content"],
        "sources": list(set(sources))
    }
