# Technical Specification

> For spec: LangChain/LangGraph Streamlit Agent

## Technical Requirements

- Python 3.12+; project managed with `uv` and `pyproject.toml`
- `agent.py` must have zero imports from `streamlit` — it is a pure agent module
- `build_agent(llm)` connects to the FastMCP server synchronously at call time using
  `langchain_mcp_adapters`; tools are loaded and bound to the compiled graph
- `run_turn(message: str, state: AgentState) -> tuple[str, AgentState]` wraps the async
  `graph.ainvoke()` call using `asyncio.run()` and returns the final AI message text
  plus the updated `AgentState`
- `AgentState` is `TypedDict` with a single `messages: list[BaseMessage]` key, matching
  the LangGraph `MessagesState` contract
- `get_llm(provider: str, model: str)` returns:
  - `ChatOllama(model=model, base_url=OLLAMA_URL)` for `"ollama"`
  - `ChatAnthropic(model=model)` for `"claude"`
  - `ChatOpenAI(model=model)` for `"openai"`
- `app.py` initialises `st.session_state` keys on first run:
  - `provider` — string, from `DEFAULT_PROVIDER` env var (default `"ollama"`)
  - `model` — string, provider's default model from env
  - `agent` — compiled LangGraph graph, built by calling `build_agent(get_llm(...))`
  - `agent_state` — `{"messages": []}` initial empty state
  - `messages` — `[]` display list of `{"role": str, "content": str}` dicts
- Sidebar selectbox values are compared to `st.session_state.provider` / `.model` on
  each rerun; if either changes, call `build_agent()` again and reset `agent_state` and
  `messages` to empty
- If `build_agent()` raises (MCP server unreachable), catch the exception, call
  `st.error()` in the sidebar, and set `st.session_state.agent = None`; the chat input
  is disabled when `agent` is `None`
- Available providers in the sidebar are filtered to those with a non-empty API key
  (or, for Ollama, always included since no key is required)
- Model lists per provider loaded from env: `OLLAMA_MODELS`, `CLAUDE_MODELS`,
  `OPENAI_MODELS` — comma-separated strings parsed at startup
- Default models: `OLLAMA_DEFAULT_MODEL`, `CLAUDE_DEFAULT_MODEL`, `OPENAI_DEFAULT_MODEL`
- System prompt loaded from `system_prompt.md` file in the same directory as `agent.py`,
  passed to `create_react_agent` as the `state_modifier` parameter
- Docker Compose: remove `api` service entirely; `frontend` service connects directly to
  `mcp-server`; `API_BASE_URL` env var removed from frontend service

## File Layout

```
frontend/
  app.py
  agent.py
  system_prompt.md
  pyproject.toml
  Dockerfile
  .env.example
tests/
  test_agent.py
  test_config.py
  conftest.py
```

## External Dependencies

- **langchain-core** — Base LangChain abstractions (messages, runnables)
  - Justification: Required by all LangChain integrations
  - Version: `>=0.3`

- **langchain-langgraph** — LangGraph `create_react_agent` and `StateGraph`
  - Justification: Provides the agentic loop replacing the manual Anthropic SDK loop
  - Version: `>=0.2`

- **langchain-mcp-adapters** — Converts FastMCP tools to LangChain `BaseTool` instances
  - Justification: Bridges the existing FastMCP server to LangGraph without rewriting tools
  - Version: `>=0.1`

- **langchain-anthropic** — `ChatAnthropic` LangChain integration
  - Justification: Claude provider support
  - Version: `>=0.3`

- **langchain-openai** — `ChatOpenAI` LangChain integration
  - Justification: OpenAI provider support
  - Version: `>=0.2`

- **langchain-ollama** — `ChatOllama` LangChain integration
  - Justification: Ollama local model support (default provider)
  - Version: `>=0.2`

- **streamlit** — Chat UI framework
  - Justification: Retained from existing frontend; no change
  - Version: `>=1.40`

- **python-dotenv** — `.env` file loading
  - Justification: Env var management for API keys and model lists
  - Version: `>=1.0`

## Key Design Decisions (from brainstorm)

1. **No FastAPI layer** — Agent runs in Streamlit process; removes a service and a
   network hop
2. **Spinner over streaming** — `st.spinner` during `run_turn()`; avoids `asyncio`
   complexity in Streamlit's rerun model
3. **Agent rebuild on model switch** — New LLM = new compiled graph; history cleared;
   simplest correct behaviour
4. **Ollama default** — Local-first; works without any API keys
5. **Model lists from env** — `PROVIDER_MODELS` comma-separated vars keep choices
   configurable without code changes
