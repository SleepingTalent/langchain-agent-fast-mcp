"""Tests for the environment-driven config module."""

import os
from unittest.mock import patch

import config


def test_models_parsed_from_env():
    with patch.dict(os.environ, {"OLLAMA_MODELS": "qwen3:14b,llama3.2"}, clear=False):
        assert config.get_available_models() == ["qwen3:14b", "llama3.2"]


def test_models_strips_whitespace():
    with patch.dict(os.environ, {"OLLAMA_MODELS": " qwen3:14b , llama3.2 "}, clear=False):
        assert config.get_available_models() == ["qwen3:14b", "llama3.2"]


def test_empty_models_env_returns_empty_list():
    env = {k: v for k, v in os.environ.items() if k != "OLLAMA_MODELS"}
    with patch.dict(os.environ, env, clear=True):
        assert config.get_available_models() == []


def test_default_model_from_env():
    with patch.dict(os.environ, {"OLLAMA_DEFAULT_MODEL": "llama3.2"}, clear=False):
        assert config.get_default_model() == "llama3.2"


def test_default_model_fallback():
    env = {k: v for k, v in os.environ.items() if k != "OLLAMA_DEFAULT_MODEL"}
    with patch.dict(os.environ, env, clear=True):
        assert config.get_default_model() == "qwen3:14b"


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
