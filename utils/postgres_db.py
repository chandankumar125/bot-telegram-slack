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
# Vibelets/ADU User ID as as input parameter: Slack User → ADU User ID.
def save_slack_connection(user_id: int, team_id: str, team_name: str, access_token: str, bot_user_id: str, slack_user_id: str, refresh_token: str = None, expires_in: int = None, email: str = None):
    """
    Saves the Slack workspace and Slack user connection to PostgreSQL.
    Saves the Company info (Team ID, Name, Token) into slack_workspaces.
    Saves the User link (Slack ID ↔ Vibelets ID) into slack_user_connections.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Upsert(Update or Insert) Slack Workspace
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
        
        # 2. Maintain 1-to-1 Linkage
        # a) Disconnect any other Slack account previously linked to this Vibelets User
        # b) Disconnect any other Vibelets User previously linked to this Slack Account (Stealing logic)
        cursor.execute("""
            UPDATE public.slack_user_connections 
            SET is_connected = FALSE, disconnected_at = NOW() 
            WHERE (user_id = %s OR slack_user_id = %s) AND is_connected = TRUE
        """, (user_id, slack_user_id))

        # 3. Insert new Connection (Partial Index handles concurrency)
        cursor.execute("""
            INSERT INTO public.slack_user_connections
            (workspace_id, user_id, slack_user_id, slack_email, is_connected, connected_at, disconnected_at)
            VALUES (%s, %s, %s, %s, TRUE, NOW(), NULL)
            ON CONFLICT (slack_user_id) WHERE is_connected = TRUE
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
    """
    Retrieves the Slack Workspace configuration (Token, Expiry) for a given Team ID.
    Internal token management. Action: Fetches the raw token for API calls.
    """
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
    """
    Internal token management
    Updates the token if it was refreshed.
    """
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
    """
    Reverse lookup. Finds the ADU User ID associated with a given Slack User ID.
    Used when a message arrives from Slack.
    Returns the Vibelets user_id so the bot knows whose data to fetch.
    """
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
    """
    Checks "Is this Vibelets User (ID: 5) connected to Slack?"
    """
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
            WHERE suc.user_id = %s AND suc.is_connected = TRUE
            ORDER BY suc.id DESC
            LIMIT 1
        """, (int(user_id),))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    except ValueError:
        logger.error(f"get_slack_connection: user_id '{user_id}' is not an integer.")
        return None
    except Exception as e:
        logger.error(f"Error in get_slack_connection: {e}")
        return None
    finally:
        if 'cursor' in locals():
             cursor.close()
        if 'conn' in locals():
             conn.close()

def disconnect_slack_connection(user_id: str):
    """
    Goal: Unlinks the user. Action: Sets is_connected = FALSE in the database. 
    It does not delete the row (allows for history/audit), just deactivates it.
    """
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
    Used for notifications.
    Finds the user, checks which Workspace they belong to, and returns that Workspace's access_token
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
            WHERE suc.slack_user_id = %s AND suc.is_connected = TRUE
        """, (slack_user_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        cursor.close()
        conn.close()

# -------------------------------------------------------------------------
# TELEGRAM DATABASE FUNCTIONS
# -------------------------------------------------------------------------

def save_telegram_connection(user_id: int, chat_id: str, username: str, first_name: str, last_name: str):
    """
    Saves or updates the connection between a Vibelets User and a Telegram User.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO public.telegram_user_connections 
            (user_id, chat_id, username, first_name, last_name, is_connected, connected_at, disconnected_at)
            VALUES (%s, %s, %s, %s, %s, TRUE, NOW(), NULL)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                chat_id = EXCLUDED.chat_id,
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                is_connected = TRUE,
                connected_at = NOW(),
                disconnected_at = NULL;
        """, (user_id, chat_id, username, first_name, last_name))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving telegram connection: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_telegram_connection(user_id: str):
    """
    Checks if a Vibelets user is connected to Telegram.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT 
                is_connected as connected,
                chat_id,
                username,
                first_name
            FROM public.telegram_user_connections
            WHERE user_id = %s AND is_connected = TRUE
        """, (int(user_id),))
        
        return dict(cursor.fetchone()) if cursor.rowcount > 0 else None
    except ValueError:
         return None
    except Exception as e:
        logger.error(f"Error getting telegram connection: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def disconnect_telegram_connection(user_id: str):
    """
    Disconnects a user from Telegram.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE public.telegram_user_connections
            SET is_connected = FALSE, disconnected_at = NOW()
            WHERE user_id = %s
        """, (int(user_id),))
        conn.commit()
        return cursor.rowcount > 0
    except ValueError:
        return False
    finally:
        cursor.close()
        conn.close()

def get_telegram_user_by_chat_id(chat_id: str):
    """
    Reverse lookup: Telegram Chat ID -> Vibelets User ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_id FROM public.telegram_user_connections
            WHERE chat_id = %s AND is_connected = TRUE
        """, (chat_id,))
        row = cursor.fetchone()
        return str(row[0]) if row else None
    finally:
        cursor.close()
        conn.close()


# -------------------------------------------------------------------------
# WHATSAPP DATABASE FUNCTIONS
# -------------------------------------------------------------------------

def save_whatsapp_connection(user_id: int, whatsapp_id: str, phone_number: str, display_name: str):
    """
    Saves or updates the connection between a Vibelets User and a WhatsApp User.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO public.whatsapp_user_connections 
            (user_id, whatsapp_id, phone_number, display_name, is_connected, connected_at, disconnected_at)
            VALUES (%s, %s, %s, %s, TRUE, NOW(), NULL)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                whatsapp_id = EXCLUDED.whatsapp_id,
                phone_number = EXCLUDED.phone_number,
                display_name = EXCLUDED.display_name,
                is_connected = TRUE,
                connected_at = NOW(),
                disconnected_at = NULL;
        """, (user_id, whatsapp_id, phone_number, display_name))
        
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error saving whatsapp connection: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_whatsapp_connection(user_id: str):
    """
    Checks if a Vibelets user is connected to WhatsApp.
    """
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cursor.execute("""
            SELECT 
                is_connected as connected,
                whatsapp_id,
                phone_number,
                display_name as name
            FROM public.whatsapp_user_connections
            WHERE user_id = %s AND is_connected = TRUE
        """, (int(user_id),))
        
        return dict(cursor.fetchone()) if cursor.rowcount > 0 else None
    except ValueError:
        return None
    except Exception as e:
        logger.error(f"Error getting whatsapp connection: {e}")
        return None
    finally:
        cursor.close()
        conn.close()

def disconnect_whatsapp_connection(user_id: str):
    """
    Disconnects a user from WhatsApp.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE public.whatsapp_user_connections
            SET is_connected = FALSE, disconnected_at = NOW()
            WHERE user_id = %s
        """, (int(user_id),))
        conn.commit()
        return cursor.rowcount > 0
    except ValueError:
        return False
    finally:
        cursor.close()
        conn.close()

def get_whatsapp_user_by_phone(whatsapp_id: str):
    """
    Reverse lookup: WhatsApp ID (Phone ID usually) -> Vibelets User ID
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT user_id FROM public.whatsapp_user_connections
            WHERE whatsapp_id = %s AND is_connected = TRUE
        """, (whatsapp_id,))
        row = cursor.fetchone()
        return str(row[0]) if row else None
    finally:
        cursor.close()
        conn.close()
