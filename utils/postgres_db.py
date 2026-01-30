import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT
import time

logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        raise e

def save_slack_connection(user_id: int, team_id: str, team_name: str, access_token: str, bot_user_id: str, slack_user_id: str, refresh_token: str = None, expires_in: int = None, email: str = None):
    """
    Saves the Slack workspace and user connection to PostgreSQL.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Upsert Slack Workspace
        expires_at = None
        if expires_in:
             import datetime
             expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

        # Upsert Workspace
        cursor.execute("""
            INSERT INTO public.slack_workspaces 
            (team_id, team_name, bot_user_id, access_token, refresh_token, token_expires_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (team_id) 
            DO UPDATE SET 
                team_name = EXCLUDED.team_name,
                bot_user_id = EXCLUDED.bot_user_id,
                access_token = EXCLUDED.access_token,
                refresh_token = EXCLUDED.refresh_token,
                token_expires_at = EXCLUDED.token_expires_at,
                updated_at = NOW(),
                is_active = TRUE
            RETURNING id;
        """, (team_id, team_name, bot_user_id, access_token, refresh_token, expires_at))
        
        workspace_id = cursor.fetchone()[0]
        
        # 2. Upsert Slack User Connection
        # user_id must be INT. If not (e.g. 'unknown'), try to handle or fail.
        # We'll allow it to fail if invalid type, as per schema.
        
        cursor.execute("""
            INSERT INTO public.slack_user_connections
            (workspace_id, user_id, slack_user_id, slack_email, is_connected, connected_at)
            VALUES (%s, %s, %s, %s, TRUE, NOW())
            ON CONFLICT (slack_user_id)
            DO UPDATE SET
                workspace_id = EXCLUDED.workspace_id,
                user_id = EXCLUDED.user_id,
                slack_email = EXCLUDED.slack_email,
                is_connected = TRUE,
                connected_at = NOW(),
                disconnected_at = NULL
            RETURNING id;
        """, (workspace_id, user_id, slack_user_id, email))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving slack connection: {e}")
        raise e
    finally:
        cursor.close()
        conn.close()

def get_team_token(team_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT access_token FROM public.slack_workspaces WHERE team_id = %s
        """, (team_id,))
        row = cursor.fetchone()
        if row:
            return row[0]
        return None
    finally:
        cursor.close()
        conn.close()

def get_team_data(team_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT 
                team_id, access_token, refresh_token, 
                token_expires_at as expires_at
            FROM public.slack_workspaces 
            WHERE team_id = %s
        """, (team_id,))
        row = cursor.fetchone()
        if row and row.get('expires_at'):
             row['expires_at'] = row['expires_at'].timestamp()
        
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()

def update_team_token(team_id: str, access_token: str, refresh_token: str, expires_in: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        import datetime
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        
        cursor.execute("""
            UPDATE public.slack_workspaces
            SET access_token = %s, refresh_token = %s, token_expires_at = %s, updated_at = NOW()
            WHERE team_id = %s
        """, (access_token, refresh_token, expires_at, team_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_vibelets_user_by_slack_id(slack_user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_id FROM public.slack_user_connections 
            WHERE slack_user_id = %s AND is_connected = TRUE
        """, (slack_user_id,))
        row = cursor.fetchone()
        if row:
            return str(row[0]) 
        return None
    finally:
        cursor.close()
        conn.close()

def get_slack_connection(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT 
                suc.is_connected as connected,
                suc.slack_user_id,
                suc.slack_email as email,
                sw.team_id,
                sw.team_name,
                sw.bot_user_id
            FROM public.slack_user_connections suc
            JOIN public.slack_workspaces sw ON sw.id = suc.workspace_id
            WHERE suc.user_id = %s
        """, (user_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    finally:
        cursor.close()
        conn.close()

def disconnect_slack_connection(user_id: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE public.slack_user_connections
            SET is_connected = FALSE, disconnected_at = NOW()
            WHERE user_id = %s
        """, (user_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    finally:
        cursor.close()
        conn.close()

def get_connection_by_slack_user_id(slack_user_id: str):
    """
    Finds the team_id and token for a given slack_user_id.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT 
                sw.team_id,
                sw.access_token,
                sw.bot_user_id
            FROM public.slack_user_connections suc
            JOIN public.slack_workspaces sw ON sw.id = suc.workspace_id
            WHERE suc.slack_user_id = %s
        """, (slack_user_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()
