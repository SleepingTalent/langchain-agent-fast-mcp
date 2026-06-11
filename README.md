# langchain-agent-fast-mcp

A conversational AI agent built with [LangGraph](https://github.com/langchain-ai/langgraph) and [Streamlit](https://streamlit.io), backed by a [FastMCP](https://github.com/jlowin/fastmcp) tool server that queries a PostgreSQL database.

---

## Architecture

```mermaid
graph LR
    User("👤 User") --> ST
    ST["Streamlit Frontend\n(LangGraph ReAct Agent)"]
    ST -->|"MCP over HTTP"| MCP["FastMCP Server\nlist_users · list_products\nsearch_users · get_low_stock_products"]
    MCP -->|SQL| PG[("PostgreSQL 16")]
    OL["Ollama\nlocal LLM"] -->|inference| ST
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

### Tasks

| Task | Description |
|---|---|
| `uv run task format` | Format code with Black |
| `uv run task lint` | Lint with Ruff |
| `uv run task unit-test` | Run unit tests (no stack required) |
| `uv run task check` | Format + lint + unit tests |
| `uv run task run-stack` | Start the full Docker stack |
| `uv run task mcp-bdd` | Spin up stack · run MCP BDD tests · tear down |
| `uv run task frontend-bdd` | Spin up stack · run frontend BDD tests in headed browser · tear down |
| `uv run task frontend-headless-bdd` | Spin up stack · run frontend BDD tests headless · tear down |
| `uv run task ci` | `check` + `mcp-bdd` |

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
├── postgres-init/
│   └── init.sql          # Schema and seed data
├── tests/
│   ├── features/         # Gherkin feature files
│   ├── bdd/              # pytest-bdd step definitions
│   ├── test_agent.py
│   └── test_config.py
├── docker-compose.yml
└── pyproject.toml
```

---

## Tests

### Unit tests

Cover `frontend/agent.py` and `frontend/config.py` in isolation with all external calls mocked. Run without a running stack.

```bash
uv run task unit-test
```

### MCP BDD tests — `tests/features/mcp_server.feature`

Integration tests that call the FastMCP server's JSON-RPC API directly. Require postgres + mcp-server to be running.

| Scenario | What is verified |
|---|---|
| Available tools are discoverable | `tools/list` returns `list_users` and `list_products` |
| List users returns seeded data | `list_users` returns ≥ 1 result with `name` and `email` fields |
| List products returns seeded data | `list_products` returns ≥ 1 result with `name` and `price` fields |
| Search users by name finds a match | `search_users` with query `Alice` returns a user whose name contains `Alice` |
| Get low stock products below threshold | `get_low_stock_products` with threshold `50` returns only products with `stock < 50` |

<details>
<summary>Feature file — <code>tests/features/mcp_server.feature</code></summary>

```gherkin
Feature: MCP Tool Server
  As the AI agent
  I want to call database tools via the MCP server
  So that I can answer questions about users and products

  Background:
    Given the MCP server is running

  Scenario: Available tools are discoverable
    When I request the list of available tools
    Then the response should include a tool named "list_users"
    And the response should include a tool named "list_products"

  Scenario: List users returns seeded data
    When I call the "list_users" tool with no arguments
    Then the result should contain at least 1 user
    And each user should have a "name" and "email" field

  Scenario: List products returns seeded data
    When I call the "list_products" tool with no arguments
    Then the result should contain at least 1 product
    And each product should have a "name" and "price" field

  Scenario: Search users by name finds a match
    When I call the "search_users" tool with query "Alice"
    Then the result should contain at least 1 user
    And the first user's "name" should contain "Alice"

  Scenario: Get low stock products below threshold
    When I call the "get_low_stock_products" tool with threshold 50
    Then the result should contain at least 1 product
    And each product's "stock" should be below 50
```

</details>

```bash
uv run task mcp-bdd
```

### Frontend BDD tests — `tests/features/frontend.feature`

Full end-to-end tests that drive the Streamlit UI via Playwright, sending real prompts through the LangGraph agent → Ollama → MCP → PostgreSQL and asserting on the chat responses. **Require the full stack and a local Ollama instance.**

| Scenario | What is verified |
|---|---|
| Agent lists users from the database | Response contains at least one seeded user name (Alice, Bob, Charlie, Diana, Eve) |
| Agent lists products from the database | Response contains at least one seeded product name (Keyboard, Hub, Headphones, etc.) |
| Agent searches for a specific user | Response contains `Alice` when asked to find users named Alice |

<details>
<summary>Feature file — <code>tests/features/frontend.feature</code></summary>

```gherkin
Feature: Frontend Agent
  As a user of the chat interface
  I want to ask the AI agent questions about users and products
  So that I can get answers backed by real database data

  Background:
    Given the Streamlit app is running and connected

  Scenario: Agent lists users from the database
    When I ask the agent "list all users"
    Then the response should mention a user name

  Scenario: Agent lists products from the database
    When I ask the agent "list all products"
    Then the response should mention a product name

  Scenario: Agent searches for a specific user
    When I ask the agent "find users named Alice"
    Then the response should contain "Alice"
```

</details>

```bash
uv run task frontend-bdd          # headed (browser visible)
uv run task frontend-headless-bdd # headless
```

---

## GitHub Actions

The CI pipeline runs on every push and pull request to `main`.

```mermaid
flowchart LR
    L["Lint\nuv run task lint"] --> T["Test\nuv run task unit-test"]
    T --> B["MCP BDD Test\nuv run task mcp-bdd"]
```

| Job | Runs | What it does |
|---|---|---|
| **Lint** | Always | Runs Ruff against `frontend/` and `tests/` |
| **Test** | After Lint passes | Runs the unit test suite (17 tests, no stack) |
| **MCP BDD Test** | After Test passes | Spins up postgres + mcp-server in Docker, runs the 5 MCP BDD scenarios, tears down |

> **Frontend BDD tests** are not wired into CI — they require a local Ollama instance which is not available on GitHub Actions runners.
