"""BDD step definitions for the MCP tool server integration tests."""

import json

import httpx
import pytest
from pytest_bdd import given, parsers, scenario, then, when

MCP_URL = "http://localhost:8001/mcp"


# ── Scenarios ─────────────────────────────────────────────────────────────────


@scenario("../features/mcp_server.feature", "Available tools are discoverable")
def test_tools_discoverable():
    pass


@scenario("../features/mcp_server.feature", "List users returns seeded data")
def test_list_users():
    pass


@scenario("../features/mcp_server.feature", "List products returns seeded data")
def test_list_products():
    pass


@scenario("../features/mcp_server.feature", "Search users by name finds a match")
def test_search_users():
    pass


@scenario("../features/mcp_server.feature", "Get low stock products below threshold")
def test_low_stock_products():
    pass


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context():
    return {}


@pytest.fixture
def mcp_session():
    """Open an MCP session and return a helper that sends JSON-RPC requests."""
    session_id: list[str] = []

    def _post(method: str, params: dict | None = None, req_id: int = 1) -> dict:
        payload: dict = {"jsonrpc": "2.0", "id": req_id, "method": method}
        if params:
            payload["params"] = params
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if session_id:
            headers["Mcp-Session-Id"] = session_id[0]
        resp = httpx.post(MCP_URL, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        if "Mcp-Session-Id" in resp.headers:
            session_id.clear()
            session_id.append(resp.headers["Mcp-Session-Id"])
        content_type = resp.headers.get("content-type", "")
        if "text/event-stream" in content_type:
            for line in resp.text.splitlines():
                line = line.strip()
                if line.startswith("data:"):
                    return json.loads(line[len("data:") :].strip())
            raise ValueError(f"No data line in SSE response: {resp.text!r}")
        return resp.json()

    # Handshake
    _post(
        "initialize",
        {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "bdd-test", "version": "0.1"},
        },
    )
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    if session_id:
        headers["Mcp-Session-Id"] = session_id[0]
    httpx.post(
        MCP_URL,
        json={"jsonrpc": "2.0", "method": "notifications/initialized"},
        headers=headers,
        timeout=10,
    )

    return _post


# ── Background ─────────────────────────────────────────────────────────────────


@given("the MCP server is running")
def mcp_running():
    resp = httpx.post(
        "http://localhost:8001/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 0,
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": "health-check", "version": "0.1"},
            },
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        },
        timeout=10,
    )
    assert resp.status_code == 200, f"MCP server not reachable: {resp.status_code}"


# ── When ──────────────────────────────────────────────────────────────────────


@when("I request the list of available tools", target_fixture="tool_names")
def request_tool_list(mcp_session):
    resp = mcp_session("tools/list")
    return [t["name"] for t in resp.get("result", {}).get("tools", [])]


@when(parsers.parse('I call the "{tool}" tool with no arguments'), target_fixture="tool_result")
def call_tool_no_args(mcp_session, tool):
    resp = mcp_session("tools/call", {"name": tool, "arguments": {}})
    content = resp.get("result", {}).get("content", [])
    text = next((c["text"] for c in content if c.get("type") == "text"), "[]")
    return json.loads(text)


@when(
    parsers.parse('I call the "search_users" tool with query "{query}"'),
    target_fixture="tool_result",
)
def call_search_users(mcp_session, query):
    resp = mcp_session("tools/call", {"name": "search_users", "arguments": {"query": query}})
    content = resp.get("result", {}).get("content", [])
    text = next((c["text"] for c in content if c.get("type") == "text"), "[]")
    return json.loads(text)


@when(
    parsers.parse('I call the "get_low_stock_products" tool with threshold {threshold:d}'),
    target_fixture="tool_result",
)
def call_low_stock(mcp_session, threshold):
    resp = mcp_session(
        "tools/call", {"name": "get_low_stock_products", "arguments": {"threshold": threshold}}
    )
    content = resp.get("result", {}).get("content", [])
    text = next((c["text"] for c in content if c.get("type") == "text"), "[]")
    return json.loads(text)


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('the response should include a tool named "{name}"'))
def tool_in_list(tool_names, name):
    assert name in tool_names, f"{name!r} not found in tools: {tool_names}"


@then("the result should contain at least 1 user")
def result_has_users(tool_result):
    assert len(tool_result) >= 1, "Expected at least 1 user in result"


@then("the result should contain at least 1 product")
def result_has_products(tool_result):
    assert len(tool_result) >= 1, "Expected at least 1 product in result"


@then('each user should have a "name" and "email" field')
def users_have_fields(tool_result):
    for user in tool_result:
        assert "name" in user and "email" in user, f"User missing fields: {user}"


@then('each product should have a "name" and "price" field')
def products_have_fields(tool_result):
    for product in tool_result:
        assert "name" in product and "price" in product, f"Product missing fields: {product}"


@then(parsers.parse('the first user\'s "name" should contain "{text}"'))
def first_user_name_contains(tool_result, text):
    assert text in tool_result[0]["name"], f"Expected {text!r} in {tool_result[0]['name']!r}"


@then(parsers.parse('each product\'s "stock" should be below {threshold:d}'))
def products_below_threshold(tool_result, threshold):
    for product in tool_result:
        assert (
            product["stock"] < threshold
        ), f"Product {product['name']!r} has stock {product['stock']} >= {threshold}"
