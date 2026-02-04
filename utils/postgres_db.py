import logging
import time

logger = logging.getLogger(__name__)

from helpers import postgresql
import datetime

# Vibelets/ADU User ID as as input parameter: Slack User → ADU User ID.
async def save_slack_connection(user_id: int, team_id: str, team_name: str, access_token: str, bot_user_id: str, slack_user_id: str, refresh_token: str = None, expires_in: int = None, email: str = None):
    """
    Saves the Slack workspace and Slack user connection to PostgreSQL.
    Implements Stealing Logic: Disconnects any other Slack account linked to this user_id
    or any other user_id linked to this slack_user_id.
    """
    try:
        # 1. Upsert Workspace
        expires_at = None
        if expires_in:
             expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)

        sql_workspace = """
            INSERT INTO public.slack_workspaces 
            (team_id, team_name, bot_user_id, access_token, refresh_token, token_expires_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, NOW())
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
        """
        rows = await postgresql.query(sql_workspace, team_id, team_name, bot_user_id, access_token, refresh_token, expires_at)
        workspace_id = rows[0]['id']
        
        # 2. Identify Conflicts (Stealing & Replacement)
        sql_conflicts = """
            SELECT suc.user_id, suc.slack_user_id, sw.team_id 
            FROM public.slack_user_connections suc
            JOIN public.slack_workspaces sw ON sw.id = suc.workspace_id
            WHERE (suc.user_id = $1 OR suc.slack_user_id = $2) AND suc.is_connected = TRUE
        """
        conflicts = await postgresql.query(sql_conflicts, user_id, slack_user_id)

        # 3. Clear Conflicts
        sql_update_conflicts = """
            UPDATE public.slack_user_connections 
            SET is_connected = FALSE, disconnected_at = NOW() 
            WHERE (user_id = $1 OR slack_user_id = $2) AND is_connected = TRUE
        """
        await postgresql.query(sql_update_conflicts, user_id, slack_user_id)

        # 4. Insert new Connection
        sql_insert_conn = """
            INSERT INTO public.slack_user_connections
            (workspace_id, user_id, slack_user_id, slack_email, is_connected, connected_at, disconnected_at)
            VALUES ($1, $2, $3, $4, TRUE, NOW(), NULL)
            ON CONFLICT (slack_user_id) WHERE is_connected = TRUE
            DO UPDATE SET
                workspace_id = EXCLUDED.workspace_id,
                user_id = EXCLUDED.user_id,
                slack_email = EXCLUDED.slack_email,
                is_connected = TRUE,
                connected_at = NOW(),
                disconnected_at = NULL
            RETURNING id;
        """
        await postgresql.query(sql_insert_conn, workspace_id, user_id, slack_user_id, email)
        
        return {"success": True, "conflicts": conflicts}
        
    except Exception as e:
        logger.error(f"Error saving slack connection: {e}")
        return {"success": False, "error": str(e)}

async def get_team_token(team_id: str):
    """
    Retrieves the Slack Workspace configuration (Token, Expiry) for a given Team ID.
    Internal token management. Action: Fetches the raw token for API calls.
    """
    try:
        sql = "SELECT access_token FROM public.slack_workspaces WHERE team_id = $1"
        rows = await postgresql.query(sql, team_id)
        if rows:
            return rows[0].get('access_token')
        return None
    except Exception as e:
        logger.error(f"Error in get_team_token: {e}")
        return None

async def get_team_data(team_id: str):
    try:
        sql = """
            SELECT 
                team_id, access_token, refresh_token, 
                token_expires_at as expires_at
            FROM public.slack_workspaces 
            WHERE team_id = $1
        """
        rows = await postgresql.query(sql, team_id)
        if rows:
            row = rows[0]
            if row.get('expires_at'):
                 row['expires_at'] = row['expires_at'].timestamp()
            return row
        return None
    except Exception as e:
        logger.error(f"Error in get_team_data: {e}")
        return None

async def update_team_token(team_id: str, access_token: str, refresh_token: str, expires_in: int):
    """
    Internal token management
    Updates the token if it was refreshed.
    """
    try:
        expires_at = datetime.datetime.now() + datetime.timedelta(seconds=expires_in)
        sql = """
            UPDATE public.slack_workspaces
            SET access_token = $1, refresh_token = $2, token_expires_at = $3, updated_at = NOW()
            WHERE team_id = $4
        """
        await postgresql.query(sql, access_token, refresh_token, expires_at, team_id)
    except Exception as e:
        logger.error(f"Error in update_team_token: {e}")

async def get_vibelets_user_by_slack_id(slack_user_id: str):
    """
    Reverse lookup. Finds the ADU User ID associated with a given Slack User ID.
    Used when a message arrives from Slack.
    Returns the Vibelets user_id so the bot knows whose data to fetch.
    """
    try:
        sql = """
            SELECT user_id FROM public.slack_user_connections 
            WHERE slack_user_id = $1 AND is_connected = TRUE
        """
        rows = await postgresql.query(sql, slack_user_id)
        if rows:
            return str(rows[0].get('user_id')) 
        return None
    except Exception as e:
        logger.error(f"Error in get_vibelets_user_by_slack_id: {e}")
        return None

async def get_slack_connection(user_id: str):
    """
    Checks "Is this Vibelets User (ID: 5) connected to Slack?"
    """
    try:
        sql = """
            SELECT 
                suc.is_connected as connected,
                suc.slack_user_id,
                suc.slack_email as email,
                sw.team_id,
                sw.team_name,
                sw.bot_user_id
            FROM public.slack_user_connections suc
            JOIN public.slack_workspaces sw ON sw.id = suc.workspace_id
            WHERE suc.user_id = $1 AND suc.is_connected = TRUE
            ORDER BY suc.id DESC
            LIMIT 1
        """
        rows = await postgresql.query(sql, int(user_id))
        return rows[0] if rows else None
    except (ValueError, Exception) as e:
        logger.error(f"Error in get_slack_connection for user_id {user_id}: {e}")
        return None

async def disconnect_slack_connection(user_id: str):
    """
    Goal: Unlinks the user. Action: Sets is_connected = FALSE in the database. 
    It does not delete the row (allows for history/audit), just deactivates it.
    """
    try:
        sql = """
            UPDATE public.slack_user_connections
            SET is_connected = FALSE, disconnected_at = NOW()
            WHERE user_id = $1
        """
        # Note: asyncpg query returns rows, for UPDATE we can check length but usually we just want to know if it ran.
        # However, our helper query() returns list of dicts.
        await postgresql.query(sql, int(user_id))
        return True
    except Exception as e:
        logger.error(f"Error in disconnect_slack_connection: {e}")
        return False

async def get_connection_by_slack_user_id(slack_user_id: str):
    """
    Finds the team_id and token for a given slack_user_id.
    Used for notifications.
    Finds the user, checks which Workspace they belong to, and returns that Workspace's access_token
    """
    try:
        sql = """
            SELECT 
                sw.team_id,
                sw.access_token,
                sw.bot_user_id
            FROM public.slack_user_connections suc
            JOIN public.slack_workspaces sw ON sw.id = suc.workspace_id
            WHERE suc.slack_user_id = $1 AND suc.is_connected = TRUE
        """
        rows = await postgresql.query(sql, slack_user_id)
        return rows[0] if rows else None
    except Exception as e:
        logger.error(f"Error in get_connection_by_slack_user_id: {e}")
        return None

# -------------------------------------------------------------------------
# TELEGRAM DATABASE FUNCTIONS
# -------------------------------------------------------------------------

async def save_telegram_connection(user_id: int, chat_id: str, username: str, first_name: str, last_name: str):
    """
    Saves or updates the connection between a Vibelets User and a Telegram User.
    Implements Stealing Logic: Disconnects any other user currently linked to this chat_id
    or any other chat_id currently linked to this user_id.
    """
    try:
        # 1. Identify Conflicts
        sql_conflicts = """
            SELECT user_id, chat_id 
            FROM public.telegram_user_connections 
            WHERE (user_id = $1 OR chat_id = $2) AND is_connected = TRUE
        """
        conflicts = await postgresql.query(sql_conflicts, user_id, chat_id)

        # 2. Clear Conflicts
        sql_clear = """
            UPDATE public.telegram_user_connections 
            SET is_connected = FALSE, disconnected_at = NOW() 
            WHERE (user_id = $1 OR chat_id = $2) AND is_connected = TRUE
        """
        await postgresql.query(sql_clear, user_id, chat_id)

        # 3. Upsert new connection
        sql_upsert = """
            INSERT INTO public.telegram_user_connections 
            (user_id, chat_id, username, first_name, last_name, is_connected, connected_at, disconnected_at)
            VALUES ($1, $2, $3, $4, $5, TRUE, NOW(), NULL)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                chat_id = EXCLUDED.chat_id,
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                is_connected = TRUE,
                connected_at = NOW(),
                disconnected_at = NULL;
        """
        await postgresql.query(sql_upsert, user_id, chat_id, username, first_name, last_name)
        
        return {"success": True, "conflicts": conflicts}
    except Exception as e:
        logger.error(f"Error saving telegram connection: {e}")
        return {"success": False, "error": str(e)}

async def get_telegram_connection(user_id: str):
    """
    Checks if a Vibelets user is connected to Telegram.
    """
    try:
        sql = """
            SELECT 
                is_connected as connected,
                chat_id,
                username,
                first_name
            FROM public.telegram_user_connections
            WHERE user_id = $1 AND is_connected = TRUE
        """
        rows = await postgresql.query(sql, int(user_id))
        return rows[0] if rows else None
    except (ValueError, Exception) as e:
        logger.error(f"Error getting telegram connection for user_id {user_id}: {e}")
        return None

async def disconnect_telegram_connection(user_id: str):
    """
    Disconnects a user from Telegram.
    """
    try:
        sql = """
            UPDATE public.telegram_user_connections
            SET is_connected = FALSE, disconnected_at = NOW()
            WHERE user_id = $1
        """
        await postgresql.query(sql, int(user_id))
        return True
    except (ValueError, Exception) as e:
        logger.error(f"Error disconnecting telegram for user_id {user_id}: {e}")
        return False

async def get_telegram_user_by_chat_id(chat_id: str):
    """
    Reverse lookup: Telegram Chat ID -> Vibelets User ID
    """
    try:
        sql = """
            SELECT user_id FROM public.telegram_user_connections
            WHERE chat_id = $1 AND is_connected = TRUE
        """
        rows = await postgresql.query(sql, chat_id)
        return str(rows[0].get('user_id')) if rows else None
    except Exception as e:
        logger.error(f"Error in get_telegram_user_by_chat_id: {e}")
        return None


# -------------------------------------------------------------------------
# WHATSAPP DATABASE FUNCTIONS
# -------------------------------------------------------------------------

async def save_whatsapp_connection(user_id: int, whatsapp_id: str, phone_number: str, display_name: str):
    """
    Saves or updates the connection between a Vibelets User and a WhatsApp User.
    Implements Stealing Logic: Disconnects any other user currently linked to this whatsapp_id
    or any other whatsapp_id currently linked to this user_id.
    """
    try:
        # 1. Identify Conflicts
        sql_conflicts = """
            SELECT user_id, whatsapp_id as chat_id
            FROM public.whatsapp_user_connections 
            WHERE (user_id = $1 OR whatsapp_id = $2) AND is_connected = TRUE
        """
        conflicts = await postgresql.query(sql_conflicts, user_id, whatsapp_id)

        # 2. Clear Conflicts
        sql_clear = """
            UPDATE public.whatsapp_user_connections 
            SET is_connected = FALSE, disconnected_at = NOW() 
            WHERE (user_id = $1 OR whatsapp_id = $2) AND is_connected = TRUE
        """
        await postgresql.query(sql_clear, user_id, whatsapp_id)

        # 3. Upsert new connection
        sql_upsert = """
            INSERT INTO public.whatsapp_user_connections 
            (user_id, whatsapp_id, phone_number, display_name, is_connected, connected_at, disconnected_at)
            VALUES ($1, $2, $3, $4, TRUE, NOW(), NULL)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                whatsapp_id = EXCLUDED.whatsapp_id,
                phone_number = EXCLUDED.phone_number,
                display_name = EXCLUDED.display_name,
                is_connected = TRUE,
                connected_at = NOW(),
                disconnected_at = NULL;
        """
        await postgresql.query(sql_upsert, user_id, whatsapp_id, phone_number, display_name)
        
        return {"success": True, "conflicts": conflicts}
    except Exception as e:
        logger.error(f"Error saving whatsapp connection: {e}")
        return {"success": False, "error": str(e)}

async def get_whatsapp_connection(user_id: str):
    """
    Checks if a Vibelets user is connected to WhatsApp.
    """
    try:
        sql = """
            SELECT 
                is_connected as connected,
                whatsapp_id,
                phone_number,
                display_name as name
            FROM public.whatsapp_user_connections
            WHERE user_id = $1 AND is_connected = TRUE
        """
        rows = await postgresql.query(sql, int(user_id))
        return rows[0] if rows else None
    except (ValueError, Exception) as e:
        logger.error(f"Error getting whatsapp connection for user_id {user_id}: {e}")
        return None

async def disconnect_whatsapp_connection(user_id: str):
    """
    Disconnects a user from WhatsApp.
    """
    try:
        sql = """
            UPDATE public.whatsapp_user_connections
            SET is_connected = FALSE, disconnected_at = NOW()
            WHERE user_id = $1
        """
        await postgresql.query(sql, int(user_id))
        return True
    except (ValueError, Exception) as e:
        logger.error(f"Error disconnecting whatsapp for user_id {user_id}: {e}")
        return False

async def get_whatsapp_user_by_phone(whatsapp_id: str):
    """
    Reverse lookup: WhatsApp ID (Phone ID usually) -> Vibelets User ID
    """
    try:
        sql = """
            SELECT user_id FROM public.whatsapp_user_connections
            WHERE whatsapp_id = $1 AND is_connected = TRUE
        """
        rows = await postgresql.query(sql, whatsapp_id)
        return str(rows[0].get('user_id')) if rows else None
    except Exception as e:
        logger.error(f"Error in get_whatsapp_user_by_phone: {e}")
        return None
