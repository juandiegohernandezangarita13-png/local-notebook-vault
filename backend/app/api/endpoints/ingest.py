import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from backend.app.core.config import settings
from backend.app.services.markdown_parser import parse_markdown_metadata

router = APIRouter()

class ChatIngestRequest(BaseModel):
    title: str
    content: str
    tags: list[str] = ["gemini-chat"]

@router.post("/chat")
def ingest_chat(payload: ChatIngestRequest, authorization: str = Header(None)):
    if authorization != f"Bearer {settings.API_AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="No autorizado.")
    
    safe_title = "".join(c for c in payload.title if c.isalnum() or c in (" ", "-", "_")).strip()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{safe_title.replace(' ', '_')}.md"
    file_path = os.path.join(settings.VAULT_DIR, filename)
    
    yaml_header = (
        "---\n"
        f"title: \"{payload.title}\"\n"
        f"date: {datetime.now().isoformat()}\n"
        f"tags: {payload.tags}\n"
        "---\n\n"
    )
    
    full_content = yaml_header + payload.content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(full_content)
        
    meta = parse_markdown_metadata(full_content)
    return {
        "status": "success",
        "file": filename,
        "path": file_path,
        "metadata": meta
    }
