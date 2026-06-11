# Brainstorm: LangChain/LangGraph Streamlit Agent

> Created: 2026-06-11
> Status: Design Exploration (not yet a formal spec)

## Problem Statement

Re-engineer the existing `ai-agent-fast-mcp` project to replace the FastAPI agent
orchestration layer with a LangGraph agent running directly inside the Streamlit app.
The existing FastMCP server (postgres-backed tools) is retained unchanged.

**Target Users:** Developer using this as a working reference implementation
**Success Criteria:** Single Streamlit service connects to FastMCP, runs a LangGraph
ReAct agent, supports runtime switching between Ollama / Claude / OpenAI, and preserves
multi-turn conversation state across Streamlit reruns via `st.session_state`.

## Approaches Considered

### Approach A: LangChain `ChatMessageHistory` + `RunnableWithMessageHistory`
Hold raw message list in `st.session_state`, pass to a `ConversationBufferMemory` or
`RunnableWithMessageHistory` each turn.
✅ Benefits: Simple, explicit, no LangGraph dependency
⚠️ Trade-offs: Manual agentic loop, harder to extend to multi-step tool chaining

### Approach B: LangGraph `StateGraph` agent stored in `st.session_state`
LangGraph manages message state internally via a compiled graph. Graph and its state
checkpoint are both stored in `st.session_state`.
✅ Benefits: Handles multi-step tool loops cleanly, idiomatic LangChain ecosystem,
extensible to more complex agent patterns
⚠️ Trade-offs: Slightly more setup; async graph requires `asyncio.run()` wrapper in
Streamlit

### Selected: Approach B
**Reasoning:** The existing app is already a multi-step agentic loop (tool calls → LLM
→ more tool calls). LangGraph models this natively. The extra setup is minimal and
pays off in clarity and extensibility.

## Design Overview

### Architecture

Three Docker services: `postgres → mcp-server → streamlit` (FastAPI service dropped).

```
frontend/
  app.py               ← Streamlit UI only; imports and calls agent.py
  agent.py             ← LangGraph agent; no Streamlit imports
  pyproject.toml
  Dockerfile
  .env / .env.example
```

`agent.py` exposes one public function:
```python
def run_turn(message: str, state: AgentState) -> tuple[str, AgentState]
```

`app.py` calls it, stores the returned `AgentState` in `st.session_state`, and renders
the response. The agent module never imports Streamlit.

### Data Flow

```
User types message
  → app.py appends to st.session_state.messages (display list)
  → calls agent.run_turn(message, st.session_state.agent_state)
      → graph.invoke({messages: [...history + new message]})
          → LLM decides → calls MCP tool(s) via langchain-mcp-adapters
          → MCP server queries postgres → returns result
          → LLM generates final response
      → returns (response_text, updated_state)
  → app.py stores updated state back into st.session_state
  → renders response in chat UI
```

`AgentState` is a LangGraph `TypedDict` with a `messages` key. Passing it through
`run_turn` keeps the graph stateless between Streamlit reruns; continuity comes
entirely from `st.session_state`.

### Key Components

**`agent.py`**
- `build_agent(llm)` — connects to FastMCP via `StreamableHTTPConnection`
  (langchain-mcp-adapters), loads tools, returns a compiled `create_react_agent` graph
- `run_turn(message, state)` — synchronous wrapper; invokes the graph with current
  message history, returns `(response_text, new_state)`
- `get_llm(provider, model)` — factory returning `ChatAnthropic`, `ChatOpenAI`, or
  `ChatOllama` based on provider string

**`app.py`**
- Sidebar: provider selectbox + model selectbox (options loaded from env at startup)
- On provider/model change: rebuild agent, clear history
- `st.session_state` keys:
  - `agent` — compiled LangGraph graph
  - `agent_state` — `{"messages": [...]}` — full LangGraph message history
  - `messages` — display-only list of `{"role", "content"}` dicts for rendering
  - `provider` / `model` — current selection

### Integration Points

- FastMCP server connected via `langchain-mcp-adapters` `StreamableHTTPConnection`
- Tools loaded once in `build_agent()`, cached on the compiled graph in `st.session_state`
- `MCP_SERVER_URL` env var controls the server address
- Provider API keys read from env; missing keys silently omit that provider from the sidebar

### Environment Configuration (`.env.example`)

```
OLLAMA_URL=http://localhost:11434
OLLAMA_DEFAULT_MODEL=qwen3:14b
OLLAMA_MODELS=qwen3:14b,llama3.2

ANTHROPIC_API_KEY=
CLAUDE_DEFAULT_MODEL=claude-sonnet-4-6
CLAUDE_MODELS=claude-sonnet-4-6,claude-opus-4-8

OPENAI_API_KEY=
OPENAI_DEFAULT_MODEL=gpt-4o-mini
OPENAI_MODELS=gpt-4o-mini,gpt-4o

MCP_SERVER_URL=http://localhost:8001
DEFAULT_PROVIDER=ollama
```

Ollama is the default provider with `qwen3:14b` as the default model.

### Error Handling

- MCP server unreachable at agent build time → `st.error` in sidebar, chat input disabled
- LLM API error during `run_turn` → catch exception, return error string, do not update
  `agent_state` (preserves conversation history)
- Provider with missing API key → omitted from sidebar selectbox entirely

### Testing Strategy

- `test_agent.py` — unit tests for `get_llm()` (mock providers) and `run_turn()`
  (mock compiled graph)
- `test_config.py` — env parsing, missing keys, default fallbacks
- Integration tests deferred (require live MCP server and LLM)

## Key Decisions

1. **No FastAPI layer:** Agent runs directly in Streamlit — removes a service, reduces
   latency, simplifies the stack
2. **Spinner over streaming:** Full response renders when the turn completes; avoids
   async complexity in Streamlit
3. **Agent rebuild on model switch:** Simplest correct behaviour — new LLM means a new
   compiled graph; history is cleared on switch
4. **Model lists from env:** `PROVIDER_MODELS` comma-separated env vars keep model
   choices configurable without code changes
5. **Ollama default:** Local-first default — works without any API keys
