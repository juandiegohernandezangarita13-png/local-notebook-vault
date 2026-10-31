import os
import glob
from functools import lru_cache

import chromadb
from chromadb.utils import embedding_functions

DEFAULT_DB_PATH = "./data/chroma_db"
BATCH_SIZE = 500


@lru_cache(maxsize=None)
def _cached_collection(db_path: str, collection_name: str):
    client = chromadb.PersistentClient(path=db_path)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return client.get_or_create_collection(
        name=collection_name, embedding_function=emb_fn
    )


def get_chroma_collection(db_path: str = DEFAULT_DB_PATH, collection_name: str = "notes"):
    return _cached_collection(db_path, collection_name)


def split_text(text: str, chunk_size: int = 150, overlap: int = 30) -> list[str]:
    words = text.split()
    if not words:
        return []
    step = max(chunk_size - overlap, 1)
    chunks = []
    for i in range(0, len(words), step):
        chunks.append(" ".join(words[i:i + chunk_size]))
        if i + chunk_size >= len(words):
            break
    return chunks


def index_vault(vault_dir: str = "./data/vault", db_path: str = DEFAULT_DB_PATH):
    collection = get_chroma_collection(db_path)
    md_files = glob.glob(os.path.join(vault_dir, "**", "*.md"), recursive=True)

    documents, metadatas, ids = [], [], []
    current_sources = set()

    for file_path in md_files:
        source = os.path.relpath(file_path, vault_dir).replace(os.sep, "/")
        current_sources.add(source)

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        # Borra los fragmentos antiguos de este archivo antes de reindexarlo
        collection.delete(where={"source": source})

        for idx, chunk in enumerate(split_text(content)):
            documents.append(chunk)
            metadatas.append({"source": source, "chunk": idx})
            ids.append(f"{source}::{idx}")

    # Borra fragmentos de archivos que ya no existen
    existing = collection.get(include=["metadatas"])
    stale_ids = [
        item_id
        for item_id, meta in zip(existing["ids"], existing["metadatas"])
        if (meta or {}).get("source") not in current_sources
    ]
    if stale_ids:
        collection.delete(ids=stale_ids)

    for start in range(0, len(documents), BATCH_SIZE):
        end = start + BATCH_SIZE
        collection.upsert(
            documents=documents[start:end],
            metadatas=metadatas[start:end],
            ids=ids[start:end],
        )

    return len(documents), len(md_files)
