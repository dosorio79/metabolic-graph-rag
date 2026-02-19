FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Keep runtime dependencies for the API image minimal.
RUN pip install --upgrade pip && pip install \
    "fastapi>=0.128.5" \
    "neo4j>=6.1.0" \
    "openai>=2.21.0" \
    "pydantic>=2.12.5" \
    "python-dotenv>=1.2.1" \
    "uvicorn>=0.40.0"

COPY backend ./backend

EXPOSE 8000

CMD ["python", "-m", "backend.app.main"]
