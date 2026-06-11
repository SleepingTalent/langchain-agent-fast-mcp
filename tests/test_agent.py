"""Tests for the LangGraph agent module."""

import os
from unittest.mock import AsyncMock, patch

from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama

import agent

# ── get_llm ──────────────────────────────────────────────────────────────────


def test_get_llm_returns_chat_ollama():
    llm = agent.get_llm("qwen3:14b")
    assert isinstance(llm, ChatOllama)


def test_get_llm_passes_model_name():
    llm = agent.get_llm("llama3.2")
    assert llm.model == "llama3.2"


def test_get_llm_uses_ollama_url():
    with patch.dict(os.environ, {"OLLAMA_URL": "http://myhost:11434"}, clear=False):
        llm = agent.get_llm("qwen3:14b")
        assert "myhost" in llm.base_url


# ── run_turn ──────────────────────────────────────────────────────────────────


def test_run_turn_returns_ai_response_text(mocker):
    ai_msg = AIMessage(content="Here are the users.")
    updated_state = {"messages": [HumanMessage(content="list users"), ai_msg]}
    mock_graph = mocker.MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value=updated_state)
    mock_llm = mocker.MagicMock()

    _patch_internals(mocker, mock_graph)

    text, _ = agent.run_turn("list users", {"messages": []}, mock_llm)
    assert text == "Here are the users."


def test_run_turn_returns_updated_state(mocker):
    ai_msg = AIMessage(content="Here are the users.")
    updated_state = {"messages": [HumanMessage(content="list users"), ai_msg]}
    mock_graph = mocker.MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value=updated_state)
    mock_llm = mocker.MagicMock()

    _patch_internals(mocker, mock_graph)

    _, new_state = agent.run_turn("list users", {"messages": []}, mock_llm)
    assert new_state == updated_state


def test_run_turn_passes_full_history_to_graph(mocker):
    existing = HumanMessage(content="hello")
    ai_msg = AIMessage(content="Hi!")
    updated_state = {"messages": [existing, HumanMessage(content="list users"), ai_msg]}
    mock_graph = mocker.MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value=updated_state)
    mock_llm = mocker.MagicMock()

    _patch_internals(mocker, mock_graph)

    agent.run_turn("list users", {"messages": [existing]}, mock_llm)

    call_messages = mock_graph.ainvoke.call_args[0][0]["messages"]
    assert len(call_messages) == 2


def test_run_turn_empty_history(mocker):
    ai_msg = AIMessage(content="Hello!")
    updated_state = {"messages": [HumanMessage(content="hi"), ai_msg]}
    mock_graph = mocker.MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value=updated_state)
    mock_llm = mocker.MagicMock()

    _patch_internals(mocker, mock_graph)

    text, _ = agent.run_turn("hi", {"messages": []}, mock_llm)
    assert text == "Hello!"


def test_run_turn_returns_empty_string_when_no_ai_message(mocker):
    updated_state = {"messages": [HumanMessage(content="hi")]}
    mock_graph = mocker.MagicMock()
    mock_graph.ainvoke = AsyncMock(return_value=updated_state)
    mock_llm = mocker.MagicMock()

    _patch_internals(mocker, mock_graph)

    text, _ = agent.run_turn("hi", {"messages": []}, mock_llm)
    assert text == ""


# ── helpers ───────────────────────────────────────────────────────────────────


def _patch_internals(mocker, mock_graph):
    """Patch MultiServerMCPClient and create_react_agent to avoid real network calls."""
    mock_client = mocker.MagicMock()
    mock_client.get_tools = AsyncMock(return_value=[mocker.MagicMock()])
    mocker.patch("agent.MultiServerMCPClient", return_value=mock_client)
    mocker.patch("agent.create_react_agent", return_value=mock_graph)
