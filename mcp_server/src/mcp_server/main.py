"""FastMCP tool server application.

Exposes database-backed tools for users and products via the
Streamable HTTP transport on port 8001.
"""

import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal
from typing import AsyncIterator

from fastmcp import FastMCP

from mcp_server.database import Database
from mcp_server.tools import products as product_tools
from mcp_server.tools import users as user_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Module-level reference so tools can access the database
_db: Database | None = None


def _serialise(obj: object) -> str:
    """JSON-serialise tool results, handling datetimes and Decimals."""

    def default(o: object) -> object:
        if isinstance(o, datetime):
            return o.isoformat()
        if isinstance(o, Decimal):
            return float(o)
        raise TypeError(f"Object of type {type(o).__name__} is not JSON serializable")

    return json.dumps(obj, default=default)


@asynccontextmanager
async def app_lifespan(app: FastMCP) -> AsyncIterator[None]:
    """Manage database lifecycle alongside the FastMCP server."""
    global _db
    db = Database()
    await db.connect()
    _db = db
    logger.info("MCP server started — database connected")
    try:
        yield
    finally:
        await db.disconnect()
        _db = None
        logger.info("MCP server stopped — database disconnected")


mcp = FastMCP("agent-tools", lifespan=app_lifespan)


# ── User tools ──────────────────────────────────────────────────────────────────


def _get_db() -> Database:
    """Return the active database instance or raise if not initialised."""
    if _db is None:
        raise RuntimeError("Database is not connected — server may still be starting up")
    return _db


@mcp.tool()
async def list_users(limit: int = 20) -> str:
    """Return all users up to the given limit.

    Args:
        limit: Maximum number of users to return (default 20).
    """
    result = await user_tools.list_users(_get_db(), limit=limit)
    return _serialise(result)


@mcp.tool()
async def get_user(user_id: int) -> str:
    """Return a single user by ID.

    Args:
        user_id: The ID of the user to retrieve.
    """
    result = await user_tools.get_user(_get_db(), user_id=user_id)
    return _serialise(result)


@mcp.tool()
async def search_users(query: str) -> str:
    """Search users by name or email (case-insensitive partial match).

    Args:
        query: The search string to match against name or email.
    """
    result = await user_tools.search_users(_get_db(), query=query)
    return _serialise(result)


# ── Product tools ───────────────────────────────────────────────────────────────


@mcp.tool()
async def list_products(limit: int = 20) -> str:
    """Return all products up to the given limit.

    Args:
        limit: Maximum number of products to return (default 20).
    """
    result = await product_tools.list_products(_get_db(), limit=limit)
    return _serialise(result)


@mcp.tool()
async def get_product(product_id: int) -> str:
    """Return a single product by ID.

    Args:
        product_id: The ID of the product to retrieve.
    """
    result = await product_tools.get_product(_get_db(), product_id=product_id)
    return _serialise(result)


@mcp.tool()
async def search_products(query: str) -> str:
    """Search products by name (case-insensitive partial match).

    Args:
        query: The search string to match against product name.
    """
    result = await product_tools.search_products(_get_db(), query=query)
    return _serialise(result)


@mcp.tool()
async def get_low_stock_products(threshold: int = 10) -> str:
    """Return products where stock is below the given threshold.

    Args:
        threshold: Stock level below which a product is considered low stock (default 10).
    """
    result = await product_tools.get_low_stock_products(_get_db(), threshold=threshold)
    return _serialise(result)


if __name__ == "__main__":  # pragma: no cover
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8001)
