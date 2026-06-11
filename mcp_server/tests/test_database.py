"""Integration tests to verify the PostgreSQL database is up and seeded correctly.

Run with: pytest tests/test_database.py -v
Requires: the postgres service from docker-compose to be running.
"""

from os import environ

import asyncpg
import pytest_asyncio

DATABASE_URL = environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/agentdb",
)


@pytest_asyncio.fixture
async def db_pool():
    """Create and yield an asyncpg connection pool, then close it."""
    pool = await asyncpg.create_pool(DATABASE_URL)
    yield pool
    await pool.close()


async def test_database_is_reachable(db_pool: asyncpg.Pool) -> None:
    """Verify that we can connect and run a basic query."""
    result = await db_pool.fetchval("SELECT 1")
    assert result == 1


async def test_users_table_exists_and_seeded(db_pool: asyncpg.Pool) -> None:
    """Verify the users table exists and has the expected seed data."""
    count = await db_pool.fetchval("SELECT count(*) FROM users")
    assert count == 5, f"Expected 5 seeded users, got {count}"


async def test_products_table_exists_and_seeded(db_pool: asyncpg.Pool) -> None:
    """Verify the products table exists and has the expected seed data."""
    count = await db_pool.fetchval("SELECT count(*) FROM products")
    assert count == 8, f"Expected 8 seeded products, got {count}"


async def test_users_have_required_columns(db_pool: asyncpg.Pool) -> None:
    """Verify the users table schema has all required columns."""
    row = await db_pool.fetchrow("SELECT id, name, email, created_at FROM users LIMIT 1")
    assert row is not None
    assert all(col in row.keys() for col in ("id", "name", "email", "created_at"))


async def test_products_have_required_columns(db_pool: asyncpg.Pool) -> None:
    """Verify the products table schema has all required columns."""
    row = await db_pool.fetchrow("SELECT id, name, price, stock, created_at FROM products LIMIT 1")
    assert row is not None
    assert all(col in row.keys() for col in ("id", "name", "price", "stock", "created_at"))
