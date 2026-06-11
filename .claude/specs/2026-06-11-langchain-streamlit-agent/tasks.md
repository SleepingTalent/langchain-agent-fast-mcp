# Spec Tasks

> Spec: LangChain/LangGraph Streamlit Agent
> Created: 2026-06-11

## Tasks

- [x] 1. Project scaffold and configuration
  - [x] 1.1 Write tests for env config parsing (model lists, defaults, missing keys)
  - [x] 1.2 Initialise `pyproject.toml` with all required dependencies (`langchain-core`, `langgraph`, `langchain-mcp-adapters`, `langchain-anthropic`, `langchain-openai`, `langchain-ollama`, `streamlit`, `python-dotenv`)
  - [x] 1.3 Create `frontend/` directory with `app.py`, `agent.py`, `system_prompt.md`, `.env.example`
  - [x] 1.4 Implement env config module — parse `OLLAMA_MODELS`, `CLAUDE_MODELS`, `OPENAI_MODELS`, `*_DEFAULT_MODEL`, `DEFAULT_PROVIDER`, `MCP_SERVER_URL`, `OLLAMA_URL` from environment; filter providers by available API keys
  - [x] 1.5 Create `tests/conftest.py` and `tests/test_config.py` with fixtures and assertions for config parsing
  - [x] 1.6 Verify all tests pass

- [x] 2. LangGraph agent module (`agent.py`)
  - [x] 2.1 Write tests for `get_llm()` (correct class returned per provider, model string passed through) and `run_turn()` (mocked compiled graph, state updated, response text extracted)
  - [x] 2.2 Implement `get_llm(provider: str, model: str)` factory returning `ChatOllama`, `ChatAnthropic`, or `ChatOpenAI`
  - [x] 2.3 Implement `build_agent(llm)` — connect to FastMCP via `langchain_mcp_adapters` `MultiServerMCPClient`, verify connectivity, return llm for use in run_turn
  - [x] 2.4 Implement `run_turn(message: str, state: AgentState, llm) -> tuple[str, AgentState]` — opens fresh MCP connection, builds and invokes agent in single asyncio.run(); extract final AI message text
  - [x] 2.5 Verify all tests pass

- [x] 3. Streamlit app (`app.py`)
  - [x] 3.1 Implement `st.session_state` initialisation block — set `provider`, `model`, `agent`, `agent_state`, `messages` on first run using config defaults
  - [x] 3.2 Implement sidebar — provider selectbox (filtered by available keys), model selectbox (options from env), detect change and rebuild agent + clear history
  - [x] 3.3 Implement MCP connection error handling — catch exception from `build_agent()`, show `st.error` in sidebar, set `agent = None`, disable chat input when `agent` is `None`
  - [x] 3.4 Implement chat loop — `st.chat_input`, append user message to display list, call `run_turn()` inside `st.spinner`, update `agent_state` and display list, render assistant response
  - [x] 3.5 Render full conversation history from `st.session_state.messages` on each rerun
  - [x] 3.6 Verify app starts with `uv run streamlit run frontend/app.py` and chat works end-to-end (manual smoke test)

- [x] 4. Docker Compose and Dockerfile
  - [x] 4.1 Write `frontend/Dockerfile` — `python:3.12-slim` base, install `uv`, copy project files, run `streamlit`
  - [x] 4.2 Update `docker-compose.yml` — remove `api` service; update `frontend` service env vars to include `MCP_SERVER_URL`, `OLLAMA_URL`, `OLLAMA_MODELS`, `CLAUDE_MODELS`, `OPENAI_MODELS` etc.; remove `API_BASE_URL`
  - [x] 4.3 Add `.dockerignore`
  - [x] 4.4 Verify `docker compose up` starts all three services (postgres, mcp-server, streamlit) and the UI is reachable at `http://localhost:8501`
