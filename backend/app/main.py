"""FastAPI application entrypoint for the retrieval API."""

from fastapi import FastAPI

from backend.app.api.routes import compounds, health, pathways, reactions


app = FastAPI(
    title="Metabolic Graph RAG API",
    version="0.1.0",
)

app.include_router(health.router, tags=["health"])
app.include_router(compounds.router, tags=["compounds"], prefix="/compounds")
app.include_router(reactions.router, tags=["reactions"], prefix="/reactions")
app.include_router(pathways.router, tags=["pathways"], prefix="/pathways")
