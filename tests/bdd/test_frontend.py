"""BDD step definitions for full-stack frontend integration tests.

Requires the full Docker stack (postgres + mcp-server + frontend) to be running
and a local Ollama instance to be available. Run locally with:

    uv run task frontend-bdd-test
"""

from playwright.sync_api import Page
from pytest_bdd import given, parsers, scenario, then, when

APP_URL = "http://localhost:8501"

# Known seed values from postgres-init/init.sql
KNOWN_USER_NAMES = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
KNOWN_PRODUCT_NAMES = ["Keyboard", "Hub", "Headphones", "Mouse", "Stand", "Webcam", "SSD"]


# ── Scenarios ─────────────────────────────────────────────────────────────────


@scenario("../features/frontend.feature", "Agent lists users from the database")
def test_agent_lists_users():
    pass


@scenario("../features/frontend.feature", "Agent lists products from the database")
def test_agent_lists_products():
    pass


@scenario("../features/frontend.feature", "Agent searches for a specific user")
def test_agent_searches_user():
    pass


# ── Background ────────────────────────────────────────────────────────────────


@given("the Streamlit app is running and connected", target_fixture="app_page")
def app_is_running(page: Page):
    """Navigate to the app and wait for the agent to connect to the MCP server."""
    page.goto(APP_URL)
    # Wait for the sidebar success message — confirms MCP connectivity
    page.wait_for_selector("text=Connected", timeout=30_000)
    return page


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('I ask the agent "{message}"'), target_fixture="response_text")
def ask_agent(app_page: Page, message: str) -> str:
    """Type a message, submit it, and wait for the assistant response."""
    page = app_page
    before_count = page.locator('[data-testid="stChatMessage"]').count()

    page.locator('[data-testid="stChatInputTextArea"]').fill(message)
    page.locator('[data-testid="stChatInputTextArea"]').press("Enter")

    # Wait for both the user echo and the assistant reply to appear
    page.wait_for_function(
        "count => document.querySelectorAll('[data-testid=\"stChatMessage\"]').length >= count",
        arg=before_count + 2,
        timeout=10_000,
    )
    # Wait for the spinner to finish (LLM + tool calls complete)
    page.wait_for_function(
        "() => document.querySelectorAll('[data-testid=\"stSpinner\"]').length === 0",
        timeout=120_000,
    )

    messages = page.locator('[data-testid="stChatMessage"]').all()
    return messages[-1].inner_text()


# ── Then ──────────────────────────────────────────────────────────────────────


@then("the response should mention a user name")
def response_mentions_user(response_text: str):
    assert any(
        name in response_text for name in KNOWN_USER_NAMES
    ), f"Expected a user name from {KNOWN_USER_NAMES} in response:\n{response_text[:500]}"


@then("the response should mention a product name")
def response_mentions_product(response_text: str):
    assert any(
        name in response_text for name in KNOWN_PRODUCT_NAMES
    ), f"Expected a product name from {KNOWN_PRODUCT_NAMES} in response:\n{response_text[:500]}"


@then(parsers.parse('the response should contain "{text}"'))
def response_contains(response_text: str, text: str):
    assert text in response_text, f"Expected {text!r} in response:\n{response_text[:500]}"
