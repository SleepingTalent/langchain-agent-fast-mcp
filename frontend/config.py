"""Environment-driven configuration for Ollama model selection."""

import os


def get_available_models() -> list[str]:
    """Return model list parsed from the OLLAMA_MODELS comma-separated env var."""
    raw = os.environ.get("OLLAMA_MODELS", "")
    return [m.strip() for m in raw.split(",") if m.strip()]


def get_default_model() -> str:
    """Return the default Ollama model, falling back to qwen3:14b."""
    return os.environ.get("OLLAMA_DEFAULT_MODEL") or "qwen3:14b"


def get_mcp_server_url() -> str:
    """Return the FastMCP server URL."""
    return os.environ.get("MCP_SERVER_URL", "http://localhost:8001")


def get_ollama_url() -> str:
    """Return the Ollama server URL."""
    return os.environ.get("OLLAMA_URL", "http://localhost:11434")
