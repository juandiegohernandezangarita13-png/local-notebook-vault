from fastapi import FastAPI
from backend.app.core.config import settings
from backend.app.api.endpoints import ingest

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend local independiente para gestión de notas Markdown, RAG y cerebro de conocimiento."
)

app.include_router(ingest.router, prefix="/api/ingest", tags=["Ingest"])

@app.get("/health")
def health_check():
    return {"status": "ok", "app": settings.PROJECT_NAME}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
