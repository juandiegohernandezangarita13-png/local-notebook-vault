import ollama

from src.indexer import get_chroma_collection, DEFAULT_DB_PATH


def _field(obj, key):
    if isinstance(obj, dict):
        return obj.get(key)
    return getattr(obj, key, None)


def list_ollama_models() -> list[str]:
    try:
        data = ollama.list()
    except Exception:
        return []
    names = []
    for m in _field(data, "models") or []:
        name = _field(m, "model") or _field(m, "name")
        if name:
            names.append(name)
    return names


def query_notes(question: str, top_k: int = 4, model: str = "llama3:latest") -> dict:
    collection = get_chroma_collection(DEFAULT_DB_PATH)

    total = collection.count()
    if total == 0:
        return {
            "answer": "Todavía no hay notas indexadas. Pulsa «Reindexar Notas» en la barra lateral.",
            "sources": [],
        }

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, total),
    )

    retrieved_docs = results.get("documents", [[]])[0]
    retrieved_meta = results.get("metadatas", [[]])[0]

    context_parts = []
    sources = []
    for doc, meta in zip(retrieved_docs, retrieved_meta):
        source_name = (meta or {}).get("source", "desconocido")
        sources.append(source_name)
        context_parts.append(f"--- Documento: {source_name} ---\n{doc}")
    context = "\n\n".join(context_parts)

    system_prompt = (
        "Eres un asistente de notas locales. "
        "Responde a la pregunta del usuario utilizando de forma estricta el contexto de las notas proporcionadas. "
        "Si la respuesta no se encuentra en las notas, dilo explícitamente y no inventes."
    )
    user_prompt = f"Contexto extraído de mis notas:\n{context}\n\nPregunta: {question}"

    try:
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
    except ollama.ResponseError:
        return {
            "answer": f"El modelo «{model}» no está disponible. Descárgalo con: ollama pull {model}",
            "sources": [],
        }
    except ConnectionError:
        return {
            "answer": "No puedo conectar con Ollama. Comprueba que está en ejecución (ollama serve).",
            "sources": [],
        }
    except Exception as e:
        return {"answer": f"Error al generar la respuesta: {e}", "sources": []}

    return {
        "answer": response["message"]["content"],
        "sources": list(dict.fromkeys(sources)),
    }
