"""Unit tests for MCP server tools with mocked database.

Tests cover user and product tool functions with a mocked asyncpg
connection pool to avoid requiring a running database.
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import asyncpg
import pytest
import pytest_asyncio

from mcp_server.database import DATABASE_URL, Database
from mcp_server.main import _serialise, app_lifespan
from mcp_server.tools.products import (
    get_low_stock_products,
    get_product,
    list_products,
    search_products,
)
from mcp_server.tools.users import get_user, list_users, search_users


def _make_record(data: dict) -> dict:
    """Create a plain dict to stand in for an asyncpg.Record.

    The tool functions call dict(row) on each record, so plain dicts
    work perfectly as test doubles.
    """
    return data


@pytest_asyncio.fixture
async def mock_db() -> Database:
    """Return a Database instance with a mocked pool."""
    db = Database.__new__(Database)
    db.pool = AsyncMock()
    return db


NOW = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)

MOCK_USERS = [
    _make_record(
        {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "created_at": NOW}
    ),
    _make_record({"id": 2, "name": "Bob Smith", "email": "bob@example.com", "created_at": NOW}),
]

MOCK_PRODUCTS = [
    _make_record(
        {
            "id": 1,
            "name": "Wireless Keyboard",
            "price": Decimal("49.99"),
            "stock": 150,
            "created_at": NOW,
        }
    ),
    _make_record(
        {"id": 2, "name": "USB-C Hub", "price": Decimal("34.99"), "stock": 75, "created_at": NOW}
    ),
    _make_record(
        {
            "id": 3,
            "name": "Webcam HD 1080p",
            "price": Decimal("59.99"),
            "stock": 0,
            "created_at": NOW,
        }
    ),
]

LOW_STOCK_PRODUCTS = [
    _make_record(
        {
            "id": 3,
            "name": "Webcam HD 1080p",
            "price": Decimal("59.99"),
            "stock": 0,
            "created_at": NOW,
        }
    ),
    _make_record(
        {
            "id": 4,
            "name": "Mechanical Pencil Set",
            "price": Decimal("12.50"),
            "stock": 3,
            "created_at": NOW,
        }
    ),
    _make_record(
        {
            "id": 5,
            "name": "Portable SSD 1TB",
            "price": Decimal("89.99"),
            "stock": 5,
            "created_at": NOW,
        }
    ),
]


# ── User tool tests ────────────────────────────────────────────────────────────


async def test_list_users_returns_results(mock_db: Database) -> None:
    """list_users should return a list of user dicts."""
    mock_db.pool.fetch = AsyncMock(return_value=MOCK_USERS)
    result = await list_users(mock_db, limit=20)

    assert len(result) == 2
    assert result[0]["name"] == "Alice Johnson"
    assert result[1]["email"] == "bob@example.com"
    mock_db.pool.fetch.assert_called_once()


async def test_get_user_not_found_raises(mock_db: Database) -> None:
    """get_user should raise ValueError when the user does not exist."""
    mock_db.pool.fetchrow = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="User with id 999 not found"):
        await get_user(mock_db, user_id=999)


async def test_get_user_returns_user(mock_db: Database) -> None:
    """get_user should return a user dict when found."""
    mock_db.pool.fetchrow = AsyncMock(return_value=MOCK_USERS[0])
    result = await get_user(mock_db, user_id=1)

    assert result["id"] == 1
    assert result["name"] == "Alice Johnson"


async def test_search_users_returns_matches(mock_db: Database) -> None:
    """search_users should return matching users."""
    mock_db.pool.fetch = AsyncMock(return_value=[MOCK_USERS[0]])
    result = await search_users(mock_db, query="alice")

    assert len(result) == 1
    assert result[0]["name"] == "Alice Johnson"


# ── Product tool tests ──────────────────────────────────────────────────────────


async def test_list_products_returns_results(mock_db: Database) -> None:
    """list_products should return a list of product dicts."""
    mock_db.pool.fetch = AsyncMock(return_value=MOCK_PRODUCTS)
    result = await list_products(mock_db, limit=20)

    assert len(result) == 3
    assert result[0]["name"] == "Wireless Keyboard"


async def test_get_product_not_found_raises(mock_db: Database) -> None:
    """get_product should raise ValueError when the product does not exist."""
    mock_db.pool.fetchrow = AsyncMock(return_value=None)

    with pytest.raises(ValueError, match="Product with id 999 not found"):
        await get_product(mock_db, product_id=999)


async def test_search_products_returns_matches(mock_db: Database) -> None:
    """search_products should return matching products."""
    mock_db.pool.fetch = AsyncMock(return_value=[MOCK_PRODUCTS[2]])
    result = await search_products(mock_db, query="webcam")

    assert len(result) == 1
    assert result[0]["name"] == "Webcam HD 1080p"


async def test_get_low_stock_products_filters_correctly(mock_db: Database) -> None:
    """get_low_stock_products should return only products below the threshold."""
    mock_db.pool.fetch = AsyncMock(return_value=LOW_STOCK_PRODUCTS)
    result = await get_low_stock_products(mock_db, threshold=10)

    assert len(result) == 3
    assert all(p["stock"] < 10 for p in result)
    # Verify sorted by stock ascending
    stocks = [p["stock"] for p in result]
    assert stocks == sorted(stocks)


# ── Error path tests ────────────────────────────────────────────────────────────


async def test_list_users_handles_db_error(mock_db: Database) -> None:
    """list_users should return an error dict when the database raises."""
    mock_db.pool.fetch = AsyncMock(side_effect=asyncpg.PostgresError("connection lost"))
    result = await list_users(mock_db)

    assert len(result) == 1
    assert "error" in result[0]
    assert "Failed to list users" in result[0]["error"]


async def test_search_users_handles_db_error(mock_db: Database) -> None:
    """search_users should return an error dict when the database raises."""
    mock_db.pool.fetch = AsyncMock(side_effect=asyncpg.PostgresError("timeout"))
    result = await search_users(mock_db, query="alice")

    assert len(result) == 1
    assert "error" in result[0]


async def test_get_user_db_error_raises_value_error(mock_db: Database) -> None:
    """get_user should raise ValueError wrapping a database exception."""
    mock_db.pool.fetchrow = AsyncMock(side_effect=asyncpg.PostgresError("db error"))

    with pytest.raises(ValueError, match="Database error fetching user"):
        await get_user(mock_db, user_id=1)


async def test_list_products_handles_db_error(mock_db: Database) -> None:
    """list_products should return an error dict when the database raises."""
    mock_db.pool.fetch = AsyncMock(side_effect=asyncpg.PostgresError("connection lost"))
    result = await list_products(mock_db)

    assert len(result) == 1
    assert "error" in result[0]
    assert "Failed to list products" in result[0]["error"]


async def test_search_products_handles_db_error(mock_db: Database) -> None:
    """search_products should return an error dict when the database raises."""
    mock_db.pool.fetch = AsyncMock(side_effect=asyncpg.PostgresError("timeout"))
    result = await search_products(mock_db, query="widget")

    assert len(result) == 1
    assert "error" in result[0]


async def test_get_product_db_error_raises_value_error(mock_db: Database) -> None:
    """get_product should raise ValueError wrapping a database exception."""
    mock_db.pool.fetchrow = AsyncMock(side_effect=asyncpg.PostgresError("db error"))

    with pytest.raises(ValueError, match="Database error fetching product"):
        await get_product(mock_db, product_id=1)


async def test_get_low_stock_products_handles_db_error(mock_db: Database) -> None:
    """get_low_stock_products should return an error dict when the database raises."""
    mock_db.pool.fetch = AsyncMock(side_effect=asyncpg.PostgresError("timeout"))
    result = await get_low_stock_products(mock_db, threshold=5)

    assert len(result) == 1
    assert "error" in result[0]


# ── Coverage gap tests ──────────────────────────────────────────────────────────


async def test_search_users_returns_empty_list(mock_db: Database) -> None:
    """search_users should return an empty list when no users match the query."""
    mock_db.pool.fetch = AsyncMock(return_value=[])
    result = await search_users(mock_db, query="zzznomatch")

    assert result == []


async def test_get_low_stock_products_zero_threshold(mock_db: Database) -> None:
    """get_low_stock_products with threshold=0 should return an empty list."""
    mock_db.pool.fetch = AsyncMock(return_value=[])
    result = await get_low_stock_products(mock_db, threshold=0)

    assert result == []


def test_serialise_handles_datetime() -> None:
    """_serialise should convert datetime objects to ISO 8601 strings."""
    data = {"created_at": NOW}
    output = _serialise(data)
    assert "2025-01-15T12:00:00+00:00" in output


def test_serialise_handles_decimal() -> None:
    """_serialise should convert Decimal objects to floats."""
    data = {"price": Decimal("49.99")}
    output = _serialise(data)
    assert "49.99" in output


def test_serialise_raises_for_unknown_type() -> None:
    """_serialise should raise TypeError for unsupported types."""
    import pytest

    with pytest.raises(TypeError):
        _serialise({"value": object()})


# ── Database guard tests ────────────────────────────────────────────────────────


async def test_database_fetch_raises_when_not_connected() -> None:
    """Database.fetch should raise RuntimeError when pool is None."""
    db = Database.__new__(Database)
    db.pool = None
    with pytest.raises(RuntimeError, match="Database not connected"):
        await db.fetch("SELECT 1")


async def test_database_fetchrow_raises_when_not_connected() -> None:
    """Database.fetchrow should raise RuntimeError when pool is None."""
    db = Database.__new__(Database)
    db.pool = None
    with pytest.raises(RuntimeError, match="Database not connected"):
        await db.fetchrow("SELECT 1")


async def test_database_fetchval_raises_when_not_connected() -> None:
    """Database.fetchval should raise RuntimeError when pool is None."""
    db = Database.__new__(Database)
    db.pool = None
    with pytest.raises(RuntimeError, match="Database not connected"):
        await db.fetchval("SELECT 1")


def test_database_init_defaults() -> None:
    """Database.__init__ should set dsn and pool defaults."""
    db = Database()
    assert db.dsn == DATABASE_URL
    assert db.pool is None


def test_database_init_custom_dsn() -> None:
    """Database.__init__ should accept a custom DSN."""
    db = Database(dsn="postgresql://user:pass@host:5432/db")
    assert db.dsn == "postgresql://user:pass@host:5432/db"


async def test_database_fetchval_with_pool() -> None:
    """Database.fetchval should delegate to the pool when connected."""
    db = Database.__new__(Database)
    db.pool = AsyncMock()
    db.pool.fetchval = AsyncMock(return_value=1)
    result = await db.fetchval("SELECT 1")
    assert result == 1


async def test_database_connect_creates_pool() -> None:
    """Database.connect should create an asyncpg pool."""
    db = Database(dsn="postgresql://localhost/test")
    mock_pool = AsyncMock()
    with patch(
        "mcp_server.database.asyncpg.create_pool", new=AsyncMock(return_value=mock_pool)
    ) as mock_create:
        await db.connect()
    mock_create.assert_called_once_with("postgresql://localhost/test")
    assert db.pool is mock_pool


async def test_database_disconnect_closes_pool() -> None:
    """Database.disconnect should close the pool when connected."""
    db = Database.__new__(Database)
    db.pool = AsyncMock()
    await db.disconnect()
    db.pool.close.assert_called_once()


async def test_database_disconnect_noop_when_not_connected() -> None:
    """Database.disconnect should do nothing when pool is None."""
    db = Database.__new__(Database)
    db.pool = None
    await db.disconnect()  # should not raise


# ── Lifespan tests ──────────────────────────────────────────────────────────────


async def test_app_lifespan_connects_and_disconnects() -> None:
    """app_lifespan should connect the database on entry and disconnect on exit."""
    mock_db = AsyncMock(spec=Database)
    with patch("mcp_server.main.Database", return_value=mock_db):
        async with app_lifespan(None):  # type: ignore[arg-type]
            mock_db.connect.assert_called_once()

        mock_db.disconnect.assert_called_once()


async def test_app_lifespan_disconnects_on_exception() -> None:
    """app_lifespan should disconnect the database even if the body raises."""
    mock_db = AsyncMock(spec=Database)
    with patch("mcp_server.main.Database", return_value=mock_db):
        with pytest.raises(RuntimeError):
            async with app_lifespan(None):  # type: ignore[arg-type]
                raise RuntimeError("something went wrong")

    mock_db.disconnect.assert_called_once()
