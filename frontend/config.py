"""Environment-driven configuration for the Ollama model and service URLs."""

import os


def get_model() -> str:
    """Return the Ollama model, falling back to llama3.2:3b."""
    return os.environ.get("OLLAMA_MODEL") or "qwen3:14b"


def get_mcp_server_url() -> str:
    """Return the FastMCP server URL."""
    return os.environ.get("MCP_SERVER_URL", "http://localhost:8001")


def get_ollama_url() -> str:
    """Return the Ollama server URL."""
    return os.environ.get("OLLAMA_URL", "http://localhost:11434")
