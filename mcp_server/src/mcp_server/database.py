"""Database connection pool management using asyncpg.

Provides a connection pool that is initialised at startup and closed at
shutdown via the FastMCP lifespan context.
"""

import logging
import os
import asyncpg

logger = logging.getLogger(__name__)

DATABASE_URL: str = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/agentdb",
)


class Database:
    """Manages an asyncpg connection pool."""

    def __init__(self, dsn: str = DATABASE_URL) -> None:
        self.dsn = dsn
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        """Create the connection pool."""
        logger.info("Connecting to database: %s", self.dsn.split("@")[-1])
        self.pool = await asyncpg.create_pool(self.dsn)
        logger.info("Database connection pool created")

    async def disconnect(self) -> None:
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def fetchval(self, query: str, *args: object) -> object:
        """Execute a query and return a single value."""
        if self.pool is None:
            raise RuntimeError("Database not connected")
        return await self.pool.fetchval(query, *args)

    async def fetchrow(self, query: str, *args: object) -> asyncpg.Record | None:
        """Execute a query and return a single row."""
        if self.pool is None:
            raise RuntimeError("Database not connected")
        return await self.pool.fetchrow(query, *args)

    async def fetch(self, query: str, *args: object) -> list[asyncpg.Record]:
        """Execute a query and return all rows."""
        if self.pool is None:
            raise RuntimeError("Database not connected")
        return await self.pool.fetch(query, *args)
