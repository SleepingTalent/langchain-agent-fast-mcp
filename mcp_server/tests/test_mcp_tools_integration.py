"""Integration tests for MCP server via Streamable HTTP transport.

These tests exercise the MCP server running as a Docker container,
connecting over the network using the FastMCP Client. They verify that
the full stack (FastMCP → tools → asyncpg → PostgreSQL) works end-to-end.

Run with: uv run task mcp-int-test
Requires: postgres and mcp-server containers running via docker-compose.
"""

import json
from os import environ

import pytest
import pytest_asyncio
from fastmcp import Client
from fastmcp.exceptions import ToolError

MCP_SERVER_URL = environ.get(
    "MCP_SERVER_URL",
    "http://localhost:8001/mcp",
)


def _parse_result(result) -> object:
    """Extract and parse JSON from a CallToolResult."""
    return json.loads(result.content[0].text)


@pytest_asyncio.fixture
async def client():
    """Connect a FastMCP client to the running MCP server container."""
    async with Client(MCP_SERVER_URL) as c:
        yield c


# ── Tool discovery ──────────────────────────────────────────────────────────────


async def test_all_tools_are_registered(client: Client) -> None:
    """Verify that all expected tools are registered on the MCP server."""
    tools = await client.list_tools()
    tool_names = {t.name for t in tools}
    expected = {
        "list_users",
        "get_user",
        "search_users",
        "list_products",
        "get_product",
        "search_products",
        "get_low_stock_products",
    }
    assert expected.issubset(tool_names), f"Missing tools: {expected - tool_names}"


# ── User tool scenarios ─────────────────────────────────────────────────────────


async def test_list_users_returns_seeded_users(client: Client) -> None:
    """list_users should return the 5 seeded users."""
    result = await client.call_tool("list_users", {"limit": 20})
    data = _parse_result(result)
    assert len(data) == 5
    names = {u["name"] for u in data}
    assert "Alice Johnson" in names
    assert "Bob Smith" in names


async def test_list_users_respects_limit(client: Client) -> None:
    """list_users with limit=2 should return exactly 2 users."""
    result = await client.call_tool("list_users", {"limit": 2})
    data = _parse_result(result)
    assert len(data) == 2


async def test_get_user_returns_correct_user(client: Client) -> None:
    """get_user should return the user with the matching ID."""
    result = await client.call_tool("get_user", {"user_id": 1})
    data = _parse_result(result)
    assert data["id"] == 1
    assert data["name"] == "Alice Johnson"
    assert data["email"] == "alice@example.com"


async def test_get_user_not_found(client: Client) -> None:
    """get_user with a non-existent ID should raise ToolError."""
    with pytest.raises(ToolError, match="not found"):
        await client.call_tool("get_user", {"user_id": 9999})


async def test_search_users_by_name(client: Client) -> None:
    """search_users should find users matching by name."""
    result = await client.call_tool("search_users", {"query": "alice"})
    data = _parse_result(result)
    assert len(data) >= 1
    assert any(u["name"] == "Alice Johnson" for u in data)


async def test_search_users_by_email(client: Client) -> None:
    """search_users should find users matching by email."""
    result = await client.call_tool("search_users", {"query": "bob@"})
    data = _parse_result(result)
    assert len(data) >= 1
    assert any(u["email"] == "bob@example.com" for u in data)


async def test_search_users_no_results(client: Client) -> None:
    """search_users with a non-matching query should return an empty list."""
    result = await client.call_tool("search_users", {"query": "zzz_no_match_zzz"})
    data = _parse_result(result)
    assert data == []


# ── Product tool scenarios ──────────────────────────────────────────────────────


async def test_list_products_returns_seeded_products(client: Client) -> None:
    """list_products should return the 8 seeded products."""
    result = await client.call_tool("list_products", {"limit": 20})
    data = _parse_result(result)
    assert len(data) == 8


async def test_list_products_respects_limit(client: Client) -> None:
    """list_products with limit=3 should return exactly 3 products."""
    result = await client.call_tool("list_products", {"limit": 3})
    data = _parse_result(result)
    assert len(data) == 3


async def test_get_product_returns_correct_product(client: Client) -> None:
    """get_product should return the product with the matching ID."""
    result = await client.call_tool("get_product", {"product_id": 1})
    data = _parse_result(result)
    assert data["id"] == 1
    assert data["name"] == "Wireless Keyboard"
    assert data["price"] == 49.99


async def test_get_product_not_found(client: Client) -> None:
    """get_product with a non-existent ID should raise ToolError."""
    with pytest.raises(ToolError, match="not found"):
        await client.call_tool("get_product", {"product_id": 9999})


async def test_search_products_by_name(client: Client) -> None:
    """search_products should find products matching by name."""
    result = await client.call_tool("search_products", {"query": "keyboard"})
    data = _parse_result(result)
    assert len(data) >= 1
    assert any(p["name"] == "Wireless Keyboard" for p in data)


async def test_search_products_case_insensitive(client: Client) -> None:
    """search_products should be case-insensitive."""
    result = await client.call_tool("search_products", {"query": "WEBCAM"})
    data = _parse_result(result)
    assert len(data) >= 1
    assert any("Webcam" in p["name"] for p in data)


async def test_search_products_no_results(client: Client) -> None:
    """search_products with a non-matching query should return an empty list."""
    result = await client.call_tool("search_products", {"query": "zzz_no_match_zzz"})
    data = _parse_result(result)
    assert data == []


async def test_get_low_stock_products_default_threshold(client: Client) -> None:
    """get_low_stock_products with default threshold should return products with stock < 10."""
    result = await client.call_tool("get_low_stock_products", {})
    data = _parse_result(result)
    assert len(data) >= 1
    assert all(p["stock"] < 10 for p in data)
    # Verify sorted by stock ascending
    stocks = [p["stock"] for p in data]
    assert stocks == sorted(stocks)


async def test_get_low_stock_products_custom_threshold(client: Client) -> None:
    """get_low_stock_products with threshold=100 should return more products."""
    result = await client.call_tool("get_low_stock_products", {"threshold": 100})
    data = _parse_result(result)
    assert all(p["stock"] < 100 for p in data)


async def test_get_low_stock_products_zero_threshold(client: Client) -> None:
    """get_low_stock_products with threshold=0 should return no products (none have negative stock)."""
    result = await client.call_tool("get_low_stock_products", {"threshold": 0})
    data = _parse_result(result)
    assert data == []


# ── Serialisation ───────────────────────────────────────────────────────────────


async def test_user_response_contains_iso_timestamp(client: Client) -> None:
    """Tool results should serialise created_at as ISO 8601 strings."""
    result = await client.call_tool("get_user", {"user_id": 1})
    data = _parse_result(result)
    # ISO 8601 timestamps contain "T"
    assert "T" in data["created_at"]


async def test_product_price_is_float(client: Client) -> None:
    """Tool results should serialise Decimal prices as floats."""
    result = await client.call_tool("get_product", {"product_id": 1})
    data = _parse_result(result)
    assert isinstance(data["price"], float)
