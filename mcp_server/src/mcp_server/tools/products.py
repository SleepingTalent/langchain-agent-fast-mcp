"""Product-related MCP tools for querying the products table."""

import logging

import asyncpg

from mcp_server.database import Database

logger = logging.getLogger(__name__)


async def list_products(db: Database, limit: int = 20) -> list[dict]:
    """Return all products up to the given limit.

    Args:
        db: Database connection instance.
        limit: Maximum number of products to return (default 20).

    Returns:
        A list of product dicts with id, name, price, stock, and created_at fields.
    """
    limit = min(limit, 1000)
    try:
        rows = await db.fetch(
            "SELECT id, name, price, stock, created_at FROM products ORDER BY id LIMIT $1",
            limit,
        )
        return [dict(row) for row in rows]
    except asyncpg.PostgresError as exc:
        logger.error("Error listing products: %s", exc)
        return [{"error": f"Failed to list products: {exc}"}]


async def get_product(db: Database, product_id: int) -> dict:
    """Return a single product by ID.

    Args:
        db: Database connection instance.
        product_id: The ID of the product to retrieve.

    Returns:
        A dict with the product's id, name, price, stock, and created_at fields.

    Raises:
        ValueError: If no product is found with the given ID.
    """
    try:
        row = await db.fetchrow(
            "SELECT id, name, price, stock, created_at FROM products WHERE id = $1",
            product_id,
        )
    except asyncpg.PostgresError as exc:
        logger.error("Error fetching product %d: %s", product_id, exc)
        raise ValueError(f"Database error fetching product {product_id}: {exc}") from exc

    if row is None:
        raise ValueError(f"Product with id {product_id} not found")
    return dict(row)


async def search_products(db: Database, query: str) -> list[dict]:
    """Search products by name using case-insensitive partial matching.

    Args:
        db: Database connection instance.
        query: The search string to match against product name.

    Returns:
        A list of matching product dicts.
    """
    try:
        escaped = query.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
        pattern = f"%{escaped}%"
        rows = await db.fetch(
            "SELECT id, name, price, stock, created_at FROM products "
            "WHERE name ILIKE $1 "
            "ORDER BY id",
            pattern,
        )
        return [dict(row) for row in rows]
    except asyncpg.PostgresError as exc:
        logger.error("Error searching products with query '%s': %s", query, exc)
        return [{"error": f"Failed to search products: {exc}"}]


async def get_low_stock_products(db: Database, threshold: int = 10) -> list[dict]:
    """Return products where stock is below the given threshold.

    Args:
        db: Database connection instance.
        threshold: Stock level below which a product is considered low stock (default 10).

    Returns:
        A list of low-stock product dicts.
    """
    try:
        rows = await db.fetch(
            "SELECT id, name, price, stock, created_at FROM products "
            "WHERE stock < $1 "
            "ORDER BY stock ASC",
            threshold,
        )
        return [dict(row) for row in rows]
    except asyncpg.PostgresError as exc:
        logger.error("Error fetching low stock products: %s", exc)
        return [{"error": f"Failed to get low stock products: {exc}"}]
