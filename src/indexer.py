import os
import glob
import chromadb
from chromadb.utils import embedding_functions

def get_chroma_collection(db_path: str = "./data/chroma_db", collection_name: str = "notes"):
    client = chromadb.PersistentClient(path=db_path)
    emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    return client.get_or_create_collection(name=collection_name, embedding_function=emb_fn)

def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def index_vault(vault_dir: str = "./data/vault", db_path: str = "./data/chroma_db"):
    collection = get_chroma_collection(db_path)
    md_files = glob.glob(f"{vault_dir}/**/*.md", recursive=True)
    
    documents = []
    metadatas = []
    ids = []
    
    for file_path in md_files:
        filename = os.path.basename(file_path)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        chunks = split_text(content)
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{filename}_{idx}"
            documents.append(chunk)
            metadatas.append({"source": filename, "chunk": idx})
            ids.append(chunk_id)

    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    return len(documents), len(md_files)
