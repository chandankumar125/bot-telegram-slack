"""
PostgreSQL Helper for database operations
"""
import os
import logging
from typing import Dict, List, Any
import asyncpg
from config import PG_DATABASE_URL

# Configure logging
logger = logging.getLogger(__name__)

# Global connection pool
_pool = None

def _get_connection_string():
    """Get PostgreSQL connection string from environment variables"""
    url = None
    if PG_DATABASE_URL:
        url = PG_DATABASE_URL
    else:
        # Build from individual components
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = int(os.getenv("POSTGRES_PORT", "5432"))
        database = os.getenv("POSTGRES_DB", "postgres")
        user = os.getenv("POSTGRES_USER", "postgres")
        password = os.getenv("POSTGRES_PASSWORD", "")
        url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    # Normalize postgres:// to postgresql:// for asyncpg
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    
    return url

async def connect() -> bool:
    """
    Connect to PostgreSQL database
    
    Returns:
        bool: True if connected successfully, False otherwise
    """
    global _pool
    try:
        connection_string = _get_connection_string()
        _pool = await asyncpg.create_pool(
            connection_string,
            min_size=10,
            max_size=20,
            command_timeout=60
        )
        
        # Test the connection
        async with _pool.acquire() as conn:
            await conn.fetchval('SELECT 1')
        
        logger.info("✅ PostgreSQL connected successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to connect to PostgreSQL: {str(e)}")
        raise RuntimeError(f"❌ Failed to connect to PostgreSQL: {str(e)}")

async def query(sql: str, *args) -> List[Dict[ Any, Any]]:
    """
    Run query on PostgreSQL database
    
    Args:
        sql: SQL query string
        *args: Query parameters
        
    Returns:
        List[Dict[str, Any]]: Query results as list of dictionaries
    """
    if _pool is None:
        await connect()
    
    try:
        async with _pool.acquire() as conn:
            rows = await conn.fetch(sql, *args)
            # Convert asyncpg.Record objects to dictionaries
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise RuntimeError(f"Query error: {str(e)}")

async def disconnect():
    """Disconnect from PostgreSQL"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("PostgreSQL connection closed")
