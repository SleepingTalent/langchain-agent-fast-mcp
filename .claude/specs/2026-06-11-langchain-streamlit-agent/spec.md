# Spec Requirements Document

> Spec: LangChain/LangGraph Streamlit Agent
> Created: 2026-06-11
> Status: approved

## Overview

Re-engineer the existing `ai-agent-fast-mcp` project into a new `langchain-agent-fast-mcp` project by replacing the FastAPI agent orchestration layer with a LangGraph ReAct agent running directly inside the Streamlit app, while retaining the existing FastMCP server and Postgres database unchanged.

## User Stories

### Query the database via natural language

As a developer, I want to type a natural language question into a chat UI, so that the agent queries the Postgres database via MCP tools and returns a clear answer without me writing any SQL.

The user opens the Streamlit app in a browser. The sidebar shows the active provider (defaulting to Ollama) and a model selectbox pre-populated from env vars. The user types a question such as "show me all users". The app displays a spinner while the LangGraph agent runs: it calls the appropriate MCP tool, receives the result, and generates a response. The response appears in the chat window. The conversation history is preserved for follow-up questions in the same session.

### Switch LLM provider at runtime

As a developer, I want to switch between Ollama, Claude, and OpenAI from the sidebar, so that I can compare model responses against the same database without restarting the app.

The user selects a different provider from the sidebar selectbox. The model selectbox updates to show only models available for that provider (loaded from env vars). On confirm, the agent is rebuilt with the new LLM, the conversation history is cleared, and the chat input is re-enabled. If the selected provider has no API key configured, it does not appear in the sidebar.

## Spec Scope

1. **LangGraph agent module (`agent.py`)** - Exposes `build_agent(llm)` and `run_turn(message, state)` with no Streamlit imports; connects to FastMCP via `langchain-mcp-adapters`.
2. **Provider factory (`agent.py`)** - `get_llm(provider, model)` returns the correct LangChain chat model for Ollama, Claude, or OpenAI based on the provider string.
3. **Streamlit app (`app.py`)** - Sidebar provider/model selector, chat UI, spinner during turns, and all state stored in `st.session_state`.
4. **Environment-driven model lists** - Each provider's available models and default model are read from `.env`; missing API keys silently omit that provider from the UI.
5. **Docker Compose update** - Remove `api` service; update `frontend` service env vars; `mcp-server` and `postgres` services unchanged.

## Out of Scope

- Streaming token-by-token output (full response renders when the turn completes)
- Persistent conversation history across browser sessions or page refreshes
- Custom system prompt editing in the UI
- Any changes to the MCP server or Postgres schema
- Authentication or multi-user support

## Expected Deliverable

1. `docker compose up` starts three services (postgres, mcp-server, streamlit); the Streamlit UI at `http://localhost:8501` accepts chat messages and returns database-backed answers via the LangGraph agent.
2. Changing the provider/model in the sidebar rebuilds the agent and clears history without restarting the app.
3. `uv run pytest` passes unit tests for `get_llm()`, `run_turn()`, and env config parsing.
