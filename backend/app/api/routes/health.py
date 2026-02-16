"""Health check endpoint skeleton."""

from fastapi import APIRouter

from backend.app.db.neo4j import ping

router = APIRouter()


@router.get("/health")
async def health_check():
    try:
        ping()
        return {"api_status": {"status": "ok"}, "neo4j_status": {"status": "ok"}}
    except Exception as exc:
        return {"api_status": {"status": "ok"}, "neo4j_status": {"status": "error", "detail": str(exc)}}
