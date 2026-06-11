"""User-related MCP tools for querying the users table."""

import logging

import asyncpg

from mcp_server.database import Database

logger = logging.getLogger(__name__)


async def list_users(db: Database, limit: int = 20) -> list[dict]:
    """Return all users up to the given limit.

    Args:
        db: Database connection instance.
        limit: Maximum number of users to return (default 20).

    Returns:
        A list of user dicts with id, name, email, and created_at fields.
    """
    limit = min(limit, 1000)
    try:
        rows = await db.fetch(
            "SELECT id, name, email, created_at FROM users ORDER BY id LIMIT $1",
            limit,
        )
        return [dict(row) for row in rows]
    except asyncpg.PostgresError as exc:
        logger.error("Error listing users: %s", exc)
        return [{"error": f"Failed to list users: {exc}"}]


async def get_user(db: Database, user_id: int) -> dict:
    """Return a single user by ID.

    Args:
        db: Database connection instance.
        user_id: The ID of the user to retrieve.

    Returns:
        A dict with the user's id, name, email, and created_at fields.

    Raises:
        ValueError: If no user is found with the given ID.
    """
    try:
        row = await db.fetchrow(
            "SELECT id, name, email, created_at FROM users WHERE id = $1",
            user_id,
        )
    except asyncpg.PostgresError as exc:
        logger.error("Error fetching user %d: %s", user_id, exc)
        raise ValueError(f"Database error fetching user {user_id}: {exc}") from exc

    if row is None:
        raise ValueError(f"User with id {user_id} not found")
    return dict(row)


async def search_users(db: Database, query: str) -> list[dict]:
    """Search users by name or email using case-insensitive partial matching.

    Args:
        db: Database connection instance.
        query: The search string to match against name or email.

    Returns:
        A list of matching user dicts.
    """
    try:
        escaped = query.replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
        pattern = f"%{escaped}%"
        rows = await db.fetch(
            "SELECT id, name, email, created_at FROM users "
            "WHERE name ILIKE $1 OR email ILIKE $1 "
            "ORDER BY id",
            pattern,
        )
        return [dict(row) for row in rows]
    except asyncpg.PostgresError as exc:
        logger.error("Error searching users with query '%s': %s", query, exc)
        return [{"error": f"Failed to search users: {exc}"}]
