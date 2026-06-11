FROM python:3.12-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

COPY src/ src/
RUN uv sync --no-dev

EXPOSE 8001

CMD ["uv", "run", "python", "-m", "mcp_server.main"]
