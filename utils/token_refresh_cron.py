import os
import sys
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from psycopg2.extras import RealDictCursor

# Add root to sys.path if not already there
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if root_dir not in sys.path:
    sys.path.append(root_dir)

from utils.postgres_db import update_team_token
from helpers.slack_api import refresh_slack_token
from helpers.telegram_api import get_telegram_me
from helpers.whatsapp_api import get_whatsapp_phone_info
from helpers import postgresql

# Configure logging
logger = logging.getLogger(__name__)

# Initialize Scheduler
scheduler = AsyncIOScheduler()

async def run_token_refresh_logic():
    """
    Unified logic to refresh Slack tokens and check Telegram/WhatsApp health.
    """
    logger.info("[Token Manager] Running scheduled refresh task...")
    
    try:

        sql_slack = """
            SELECT team_id, team_name, refresh_token 
            FROM public.slack_workspaces 
            WHERE token_expires_at <= NOW() + INTERVAL '2 hours'
            AND refresh_token IS NOT NULL
            AND is_active = TRUE
        """
        expiring_teams = await postgresql.query(sql_slack)
        
        for team in expiring_teams:
            try:
                logger.info(f"[Slack] Refreshing token for: {team['team_name']}")
                new_data = refresh_slack_token(team['refresh_token'])
                await update_team_token(
                    team_id=team['team_id'],
                    access_token=new_data['access_token'],
                    refresh_token=new_data['refresh_token'],
                    expires_in=new_data['expires_in']
                )
                logger.info(f"[Slack] ✅ Refreshed: {team['team_name']}")
            except Exception as e:
                logger.error(f"[Slack] ❌ Failed {team['team_id']}: {e}")

        # 2. TELEGRAM WATCHDOG
        try:
            get_telegram_me()
            logger.info("[Telegram] ✅ Token Healthy")
        except Exception as e:
            logger.error(f"[Telegram] ❌ Health Check Failed: {e}")

        # 3. WHATSAPP WATCHDOG
        try:
            get_whatsapp_phone_info()
            logger.info("[WhatsApp] ✅ Token Healthy")
        except Exception as e:
            logger.error(f"[WhatsApp] ❌ Health Check Failed: {e}")


    except Exception as e:
        logger.error(f"[Token Manager] Critical logic error: {e}")

def start_token_scheduler():
    """
    Starts the APScheduler to run the refresh logic every 30 minutes.
    """
    logger.info("Initializing Token Manager Scheduler...")
    
    # Run every 30 minutes
    scheduler.add_job(
        run_token_refresh_logic, 
        'cron', 
        minute='*/30',
        id='unified_token_refresh',
        replace_existing=True
    )
    
    # Run once immediately on startup
    scheduler.add_job(
        run_token_refresh_logic,
        id='startup_refresh_check'
    )
    
    scheduler.start()
    logger.info("✅ Token Manager Scheduler started (Frequency: 30m).")

def stop_token_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Token Manager Scheduler shut down.")

if __name__ == "__main__":
    # Setup basic logging for standalone run
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    import asyncio
    asyncio.run(run_token_refresh_logic())
