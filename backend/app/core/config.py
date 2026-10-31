import os
from pydantic import BaseModel

class Settings(BaseModel):
    PROJECT_NAME: str = "Local Notebook Vault"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    
    # Rutas relativas locales
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    VAULT_DIR: str = os.path.join(BASE_DIR, "data", "vault")
    CHROMA_DIR: str = os.path.join(BASE_DIR, "data", "chroma_db")
    
    # Modelo local por defecto
    DEFAULT_MODEL: str = "llama3:latest"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    # Clave de seguridad local para aceptar ingesta externa de chats
    API_AUTH_TOKEN: str = os.getenv("VAULT_API_TOKEN", "local-secure-token-123")

settings = Settings()
os.makedirs(settings.VAULT_DIR, exist_ok=True)
os.makedirs(settings.CHROMA_DIR, exist_ok=True)
