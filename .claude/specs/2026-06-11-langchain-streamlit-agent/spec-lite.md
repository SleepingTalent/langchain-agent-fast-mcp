# Spec Summary (Lite)

Replace the FastAPI agent layer in `ai-agent-fast-mcp` with a LangGraph `create_react_agent` running directly inside a Streamlit app (`app.py`), with all agent logic isolated in a separate `agent.py` module (no Streamlit imports) that connects to the existing FastMCP server via `langchain-mcp-adapters`. The Streamlit sidebar lets the user switch between Ollama (default), Claude, and OpenAI at runtime using model lists loaded from env vars; the compiled LangGraph graph, its message state, and the display message list are all stored in `st.session_state`.
