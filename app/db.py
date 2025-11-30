# app/db.py
import asyncpg
from app.settings import DATABASE_URL

pool: asyncpg.pool.Pool | None = None

async def init_db():
    """Initializes the database connection pool."""
    global pool
    if not pool:
        pool = await asyncpg.create_pool(DATABASE_URL)

async def close_db():
    """Closes the database connection pool."""
    global pool
    if pool:
        await pool.close()
        pool = None

async def save_comment(target: str, text: str, user_id: int):
    """
    Saves a comment to the database and updates the user's last comment time.
    This runs as a single transaction.
    """
    if not pool:
        raise ConnectionError("Database pool is not initialized. Call init_db() first.")

    async with pool.acquire() as conn:
        async with conn.transaction():
            # Insert the new comment
            await conn.execute(
                """
                INSERT INTO comments (target, comment_text, from_user_id)
                VALUES ($1, $2, $3)
                """,
                target, text, user_id
            )
            # Update the user's last comment timestamp.
            # If the user doesn't exist, create them.
            await conn.execute(
                """
                INSERT INTO users (id, last_comment_at)
                VALUES ($1, now())
                ON CONFLICT (id) DO UPDATE SET last_comment_at = now()
                """,
                user_id
            )

async def get_user_last_comment(user_id: int):
    """
    Retrieves the last comment timestamp and blocked status for a user.
    """
    if not pool:
        raise ConnectionError("Database pool is not initialized. Call init_db() first.")
        
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT last_comment_at, blocked FROM users WHERE id=$1", user_id)
        return row
