# langchain-agent-fast-mcp

A conversational AI agent built with [LangGraph](https://github.com/langchain-ai/langgraph) and [Streamlit](https://streamlit.io), backed by a [FastMCP](https://github.com/jlowin/fastmcp) tool server that queries a PostgreSQL database.

---

## Architecture

```
┌─────────────────────┐        MCP (HTTP)       ┌──────────────────────┐
│  Streamlit frontend │ ──────────────────────▶  │  FastMCP server      │
│  (LangGraph agent)  │                          │  (users + products)  │
└─────────────────────┘                          └──────────┬───────────┘
                                                            │ SQL
                                                 ┌──────────▼───────────┐
                                                 │  PostgreSQL 16        │
                                                 └──────────────────────┘
```

- **Frontend** — Streamlit chat UI. Agent logic lives in `frontend/agent.py` (no Streamlit imports); `frontend/app.py` wires it into the UI and stores all state in `st.session_state`.
- **Agent** — `create_react_agent` from LangGraph, using [langchain-mcp-adapters](https://github.com/langchain-ai/langchain-mcp-adapters) to expose the FastMCP tools as LangChain tools.
- **MCP server** — FastMCP HTTP server exposing four tools: `list_users`, `list_products`, `search_users`, `get_low_stock_products`.
- **LLM** — [Ollama](https://ollama.com) running locally (default model: `qwen3:14b`). Configurable via environment variables.

---

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [Ollama](https://ollama.com) running locally with at least one model pulled, e.g.:
  ```bash
  ollama pull qwen3:14b
  ```
- [uv](https://docs.astral.sh/uv/) for local development

---

## Quick start

```bash
# 1. Clone the repo
git clone https://github.com/SleepingTalent/langchain-agent-fast-mcp.git
cd langchain-agent-fast-mcp

# 2. Copy and edit environment config
cp .env.example .env
# edit .env — set OLLAMA_URL, OLLAMA_DEFAULT_MODEL, OLLAMA_MODELS as needed

# 3. Start the full stack
docker compose up --build

# 4. Open the UI
open http://localhost:8501
```

---

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_DB` | `agentdb` | PostgreSQL database name |
| `POSTGRES_USER` | `postgres` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `DATABASE_URL` | `postgresql://postgres:postgres@postgres:5432/agentdb` | Full DB URL (used by MCP server) |
| `MCP_SERVER_URL` | `http://localhost:8001` | MCP server base URL (used by frontend) |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama API base URL |
| `OLLAMA_DEFAULT_MODEL` | `qwen3:14b` | Model selected on startup |
| `OLLAMA_MODELS` | `qwen3:14b,llama3.2:3b` | Comma-separated list of models shown in the sidebar |

When running via Docker Compose, the frontend connects to Ollama on the host via `host.docker.internal`. Set `OLLAMA_URL=http://host.docker.internal:11434` in your `.env` if needed.

---

## Development

### Install dependencies

```bash
uv sync
```

### Available tasks

```bash
uv run task check        # format + lint + unit tests
uv run task format       # black
uv run task lint         # ruff
uv run task unit-test    # pytest (excludes BDD tests)
uv run task run-stack    # docker compose up --build
uv run task bdd-test     # spin up stack, run BDD tests, tear down
uv run task ci           # check + bdd-test
```

### Project structure

```
langchain-agent-fast-mcp/
├── frontend/
│   ├── agent.py          # LangGraph agent (no Streamlit imports)
│   ├── app.py            # Streamlit UI
│   ├── config.py         # Environment config helpers
│   ├── system_prompt.md  # Agent system prompt
│   └── Dockerfile
├── mcp_server/
│   └── src/mcp_server/
│       ├── main.py       # FastMCP server entry point
│       └── tools/        # users + products tool definitions
├── docker/
│   └── init.sql          # Schema and seed data
├── tests/
│   ├── features/         # Gherkin feature files
│   ├── bdd/              # pytest-bdd step definitions
│   ├── test_agent.py
│   └── test_config.py
├── docker-compose.yml
└── pyproject.toml
```

### Running tests

```bash
# Unit tests only (no stack required)
uv run task unit-test

# BDD integration tests (spins up Docker stack automatically)
uv run task bdd-test
```
