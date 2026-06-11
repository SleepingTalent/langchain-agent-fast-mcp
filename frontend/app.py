"""Streamlit chat UI for the LangGraph agent.

Imports all agent logic from agent.py — this file contains only UI code.
Agent state, LLM object, and display messages are persisted in st.session_state.
"""

import streamlit as st

import config
from agent import AgentState, build_agent, get_llm, run_turn

st.set_page_config(page_title="AI Agent", page_icon="🤖", layout="centered")
st.title("AI Agent")

# ── Session state initialisation (first load only) ────────────────────────────

if "model" not in st.session_state:
    st.session_state.model = config.get_default_model()
    st.session_state.agent_state: AgentState = {"messages": []}
    st.session_state.messages: list[dict] = []
    st.session_state.agent_error: str | None = None

    try:
        st.session_state.agent = build_agent(get_llm(st.session_state.model))
    except Exception as exc:
        st.session_state.agent = None
        st.session_state.agent_error = str(exc)

# ── Sidebar — model selector ───────────────────────────────────────────────────

with st.sidebar:
    st.header("Settings")

    model_options = config.get_available_models() or [config.get_default_model()]
    current_model = (
        st.session_state.model if st.session_state.model in model_options else model_options[0]
    )
    selected_model = st.selectbox(
        "Model",
        options=model_options,
        index=model_options.index(current_model),
    )

    # Rebuild agent on model change; clear conversation history
    if selected_model != st.session_state.model:
        st.session_state.model = selected_model
        st.session_state.agent_state = {"messages": []}
        st.session_state.messages = []
        st.session_state.agent_error = None

        try:
            st.session_state.agent = build_agent(get_llm(selected_model))
        except Exception as exc:
            st.session_state.agent = None
            st.session_state.agent_error = str(exc)

    if st.session_state.agent_error:
        st.error(f"MCP connection failed: {st.session_state.agent_error}")
    elif st.session_state.agent is not None:
        st.success(f"Connected · {selected_model}")

# ── Conversation history ───────────────────────────────────────────────────────

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ─────────────────────────────────────────────────────────────────

if prompt := st.chat_input(
    "Ask something about users or products…",
    disabled=st.session_state.agent is None,
):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                response_text, new_state = run_turn(
                    prompt,
                    st.session_state.agent_state,
                    st.session_state.agent,
                )
                st.session_state.agent_state = new_state
            except Exception as exc:
                response_text = f"⚠️ Error: {exc}"

        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})
