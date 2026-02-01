import requests
import google.generativeai as genai
from config import VIBELETS_BASE_URL, VIBELETS_API_KEY, GEMINI_API_KEY

from utils.postgres_db import get_slack_connection
from utils.db import get_telegram_connection

# resolve_query: used by slack_service.py, telegram_service.py, whatsapp_service.py
def resolve_query(user_id, question, context: dict = None):
    # DUMMY/TEST MODE:
    # If the user asks for a test or the API key is not set up, act as an AI Agent.
    is_dummy_request = any(k in question.lower() for k in ["dummy", "test", "check", "ping"])
    is_invalid_key = not VIBELETS_API_KEY or VIBELETS_API_KEY == "your-vibelets-api-key"

    if is_dummy_request or is_invalid_key:
        # Try using Gemini if available
        if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                # Use 'gemini-2.0-flash' as it was recognized
                model = genai.GenerativeModel('gemini-2.0-flash')
                
                # Enrich prompt with context if available
                prompt = f"You are the Vibelets AI Bot. Answer this user query concisely: {question}"
                if context and context.get("alert_id"):
                     prompt += f"\n\nContext: The user is replying to Alert ID: {context.get('alert_id')}"
                
                response = model.generate_content(prompt)
                return f"✨ *[Gemini AI]*\n{response.text}"
            except Exception as e:
                # Log the real error to console, but show a nice message to user
                print(f"------------ GEMINI ERROR ------------")
                print(e)
                print(f"--------------------------------------")
                return (
                    f"🤖 *[System Message]*\n"
                    f"I am currently upgrading my brain. 🧠\n"
                    f"Please try again later or contact support.\n"
                    f"Error: {str(e)}"
                )

        # Fallback to static dummy text (only if NO key is present)
        return (
            f"🤖 *[Dummy Agent]*\n"
            f"I received your query: _'{question}'_\n\n"
            f"✅ **System Status:** Operational"
        )
    
    try:
        payload = {"user_id": user_id, "question": question}
        if context:
            payload["context"] = context

        response = requests.post(
            f"{VIBELETS_BASE_URL}/bot/resolve",
            headers={"Authorization": f"Bearer {VIBELETS_API_KEY}"},
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("answer", "No response found")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Vibelets AI: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

# push_notification: used by routers/notifications.py
async def push_notification(payload):
    msg = f"*{payload.title}*\n{payload.summary}"
    results = {}
    
    # 1. Determine Targets
    targets = []
    
    # If user_id provided, look up their connections
    if payload.user_id:
        
        # Check Slack
        if payload.platform in ["slack", "all"]:
            slack_conn = get_slack_connection(payload.user_id)
            print(f"DEBUG: Checking Slack connection for {payload.user_id}: {slack_conn}")
            if slack_conn and slack_conn.get("connected"):
                targets.append(("slack", slack_conn.get("slack_user_id")))
        
        # Check Telegram
        if payload.platform in ["telegram", "all"]:
            tg_conn = get_telegram_connection(payload.user_id)
            if tg_conn and tg_conn.get("connected"):
                targets.append(("telegram", tg_conn.get("chat_id")))
                
    # If explicit channel_id provided (Legacy/Direct mode)
    elif payload.channel_id:
        targets.append((payload.platform, payload.channel_id))
        
    # 2. Dispatch
    from services.slack_service import send_message_to_user as slack_send_message
    from services.telegram_service import send_message as telegram_send_message
    import asyncio
    
    for platform, target_id in targets:
        try:
            if platform == "slack":
                loop = asyncio.get_event_loop()
                # Run sync wrapper in thread
                res = await loop.run_in_executor(None, slack_send_message, target_id, msg)
                if isinstance(res, dict) and not res.get("ok"):
                    results["slack"] = f"failed: {res.get('error')}"
                else:
                    results["slack"] = "sent"
            elif platform == "telegram":
                await telegram_send_message(target_id, msg)
                results["telegram"] = "sent"
        except Exception as e:
            results[platform] = f"failed: {str(e)}"
            
    return results if results else {"status": "skipped", "reason": "No connected platforms found for user"}
