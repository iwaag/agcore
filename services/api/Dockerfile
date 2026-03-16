FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src:/app/worker_src:/app/packages/domain/src:/app/packages/infra/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock* /app/

RUN uv sync --frozen --no-install-project

COPY services/api/src /app/src
COPY services/worker/src /app/worker_src
COPY packages/domain/src /app/packages/domain/src
COPY packages/infra/src /app/packages/infra/src
COPY services/api/entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
