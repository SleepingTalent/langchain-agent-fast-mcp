"""LangGraph agent module.

Exposes three public functions used by app.py:
  - get_llm      — construct a ChatOllama instance for the given model
  - build_agent  — verify MCP connectivity and return the LLM ready for use
  - run_turn     — run one conversation turn against the agent and return the response
"""

import asyncio
from pathlib import Path
from typing import Annotated, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_ollama import ChatOllama
from langgraph.graph.message import add_messages
from langchain.agents import create_agent

import config


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def get_llm(model: str) -> ChatOllama:
    """Return a ChatOllama instance for the given model name."""
    return ChatOllama(model=model, base_url=config.get_ollama_url())


def build_agent(llm: ChatOllama) -> ChatOllama:
    """Verify MCP server connectivity and return the LLM for use in run_turn.

    Raises if the MCP server is unreachable so app.py can surface an error early.
    """

    async def _check() -> None:
        client = MultiServerMCPClient(
            {"agent-tools": {"url": f"{config.get_mcp_server_url()}/mcp", "transport": "http"}}
        )
        await client.get_tools()

    asyncio.run(_check())
    return llm


def run_turn(
    message: str,
    state: AgentState,
    llm: ChatOllama,
) -> tuple[str, AgentState]:
    """Run one conversation turn and return (response_text, updated_state).

    Opens a fresh MCP connection, builds the agent, and invokes it with the full
    message history in a single asyncio.run() call to avoid event-loop conflicts.
    """

    async def _run() -> AgentState:
        client = MultiServerMCPClient(
            {"agent-tools": {"url": f"{config.get_mcp_server_url()}/mcp", "transport": "http"}}
        )
        tools = await client.get_tools()
        graph = create_agent(llm, tools, system_prompt=_load_system_prompt())
        messages = list(state.get("messages", [])) + [{"role": "user", "content": message}]
        return await graph.ainvoke({"messages": messages})

    new_state: AgentState = asyncio.run(_run())

    for msg in reversed(new_state["messages"]):
        if isinstance(msg, AIMessage):
            return str(msg.content), new_state

    return "", new_state


def _load_system_prompt() -> str:
    """Load the system prompt from system_prompt.md next to this file."""
    return (Path(__file__).parent / "system_prompt.md").read_text()
