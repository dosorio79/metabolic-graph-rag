"""FastAPI application entrypoint for the retrieval API."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.app.api.routes import compounds, health, pathways, rag, reactions
from backend.app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Metabolic Graph RAG API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_allowed_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(compounds.router, tags=["compounds"], prefix="/compounds")
app.include_router(reactions.router, tags=["reactions"], prefix="/reactions")
app.include_router(pathways.router, tags=["pathways"], prefix="/pathways")
app.include_router(rag.router, tags=["rag"], prefix="/rag")


if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level,
    )
