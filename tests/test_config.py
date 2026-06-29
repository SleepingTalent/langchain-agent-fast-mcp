"""Tests for the environment-driven config module."""

import os
from unittest.mock import patch

import config


def test_model_from_env():
    with patch.dict(os.environ, {"OLLAMA_MODEL": "llama3.2:3b"}, clear=False):
        assert config.get_model() == "llama3.2:3b"


def test_model_fallback():
    env = {k: v for k, v in os.environ.items() if k != "OLLAMA_MODEL"}
    with patch.dict(os.environ, env, clear=True):
        assert config.get_model() == "qwen3:14b"


def test_model_custom_override():
    with patch.dict(os.environ, {"OLLAMA_MODEL": "mistral:7b"}, clear=False):
        assert config.get_model() == "mistral:7b"


def test_mcp_server_url_from_env():
    with patch.dict(os.environ, {"MCP_SERVER_URL": "http://custom:9000"}, clear=False):
        assert config.get_mcp_server_url() == "http://custom:9000"


def test_mcp_server_url_fallback():
    env = {k: v for k, v in os.environ.items() if k != "MCP_SERVER_URL"}
    with patch.dict(os.environ, env, clear=True):
        assert config.get_mcp_server_url() == "http://localhost:8001"


def test_ollama_url_from_env():
    with patch.dict(os.environ, {"OLLAMA_URL": "http://custom:11434"}, clear=False):
        assert config.get_ollama_url() == "http://custom:11434"


def test_ollama_url_fallback():
    env = {k: v for k, v in os.environ.items() if k != "OLLAMA_URL"}
    with patch.dict(os.environ, env, clear=True):
        assert config.get_ollama_url() == "http://localhost:11434"
