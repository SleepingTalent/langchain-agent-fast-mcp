"""Unit tests for mcp_server/main.py helper functions, tool handlers, and Database class.

Tests _serialise, _get_db, and each MCP tool handler with a mocked database.
"""

import json
from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import mcp_server.main as main_module
from mcp_server.main import _get_db, _serialise
from mcp_server.database import Database

NOW = datetime(2025, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


# ── _serialise ───────────────────────────────────────────────────────────────────


def test_serialise_plain_data() -> None:
    assert _serialise({"key": "value"}) == '{"key": "value"}'


def test_serialise_datetime() -> None:
    result = json.loads(_serialise({"created_at": NOW}))
    assert result["created_at"] == NOW.isoformat()


def test_serialise_decimal() -> None:
    result = json.loads(_serialise({"price": Decimal("49.99")}))
    assert result["price"] == pytest.approx(49.99)


def test_serialise_unknown_type_raises() -> None:
    with pytest.raises(TypeError):
        _serialise({"bad": object()})


# ── _get_db ───────────────────────────────────────────────────────────────────────


def test_get_db_raises_when_not_connected() -> None:
    with patch.object(main_module, "_db", None):
        with pytest.raises(RuntimeError, match="Database is not connected"):
            _get_db()


def test_get_db_returns_db_when_connected() -> None:
    mock_db = MagicMock(spec=Database)
    with patch.object(main_module, "_db", mock_db):
        result = _get_db()
    assert result is mock_db


# ── Tool handler fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def mock_db() -> Database:
    db = Database.__new__(Database)
    db.pool = AsyncMock()
    return db


USER_ROW = {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "created_at": NOW}
PRODUCT_ROW = {
    "id": 1,
    "name": "Keyboard",
    "price": Decimal("49.99"),
    "stock": 100,
    "created_at": NOW,
}


# ── User tool handlers ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_users_handler(mock_db: Database) -> None:
    mock_db.pool.fetch = AsyncMock(return_value=[USER_ROW])
    with patch.object(main_module, "_db", mock_db):
        result = await main_module.list_users(limit=10)
    data = json.loads(result)
    assert data[0]["name"] == "Alice Johnson"


@pytest.mark.asyncio
async def test_get_user_handler(mock_db: Database) -> None:
    mock_db.pool.fetchrow = AsyncMock(return_value=USER_ROW)
    with patch.object(main_module, "_db", mock_db):
        result = await main_module.get_user(user_id=1)
    data = json.loads(result)
    assert data["name"] == "Alice Johnson"


@pytest.mark.asyncio
async def test_search_users_handler(mock_db: Database) -> None:
    mock_db.pool.fetch = AsyncMock(return_value=[USER_ROW])
    with patch.object(main_module, "_db", mock_db):
        result = await main_module.search_users(query="alice")
    data = json.loads(result)
    assert len(data) == 1


# ── Product tool handlers ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_products_handler(mock_db: Database) -> None:
    mock_db.pool.fetch = AsyncMock(return_value=[PRODUCT_ROW])
    with patch.object(main_module, "_db", mock_db):
        result = await main_module.list_products(limit=10)
    data = json.loads(result)
    assert data[0]["name"] == "Keyboard"


@pytest.mark.asyncio
async def test_get_product_handler(mock_db: Database) -> None:
    mock_db.pool.fetchrow = AsyncMock(return_value=PRODUCT_ROW)
    with patch.object(main_module, "_db", mock_db):
        result = await main_module.get_product(product_id=1)
    data = json.loads(result)
    assert data["name"] == "Keyboard"


@pytest.mark.asyncio
async def test_search_products_handler(mock_db: Database) -> None:
    mock_db.pool.fetch = AsyncMock(return_value=[PRODUCT_ROW])
    with patch.object(main_module, "_db", mock_db):
        result = await main_module.search_products(query="keyboard")
    data = json.loads(result)
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_low_stock_products_handler(mock_db: Database) -> None:
    low_stock = {**PRODUCT_ROW, "stock": 3}
    mock_db.pool.fetch = AsyncMock(return_value=[low_stock])
    with patch.object(main_module, "_db", mock_db):
        result = await main_module.get_low_stock_products(threshold=10)
    data = json.loads(result)
    assert data[0]["stock"] == 3


@pytest.mark.asyncio
async def test_handler_raises_when_db_not_connected() -> None:
    with patch.object(main_module, "_db", None):
        with pytest.raises(RuntimeError, match="Database is not connected"):
            await main_module.list_users()


# ── Database class ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_database_connect_and_disconnect() -> None:
    """Database.connect should create a pool; disconnect should close it."""
    mock_pool = AsyncMock()

    with patch("mcp_server.database.asyncpg.create_pool", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_pool
        from mcp_server.database import Database

        db = Database(dsn="postgresql://fake/db")
        await db.connect()
        assert db.pool is mock_pool

        await db.disconnect()
        mock_pool.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_database_fetchval() -> None:
    """Database.fetchval should delegate to pool.fetchval."""
    from mcp_server.database import Database

    db = Database.__new__(Database)
    db.pool = AsyncMock()
    db.pool.fetchval = AsyncMock(return_value=42)

    result = await db.fetchval("SELECT 1")
    assert result == 42
    db.pool.fetchval.assert_awaited_once_with("SELECT 1")


@pytest.mark.asyncio
async def test_database_fetchrow() -> None:
    """Database.fetchrow should delegate to pool.fetchrow."""
    from mcp_server.database import Database

    db = Database.__new__(Database)
    db.pool = AsyncMock()
    db.pool.fetchrow = AsyncMock(return_value={"id": 1})

    result = await db.fetchrow("SELECT * FROM users WHERE id = $1", 1)
    assert result == {"id": 1}


@pytest.mark.asyncio
async def test_database_fetch() -> None:
    """Database.fetch should delegate to pool.fetch."""
    from mcp_server.database import Database

    db = Database.__new__(Database)
    db.pool = AsyncMock()
    db.pool.fetch = AsyncMock(return_value=[{"id": 1}, {"id": 2}])

    result = await db.fetch("SELECT * FROM users")
    assert len(result) == 2
