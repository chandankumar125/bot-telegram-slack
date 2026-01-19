import requests
import google.generativeai as genai
from config import VIBELETS_BASE_URL, VIBELETS_API_KEY, GEMINI_API_KEY

def resolve_query(user_id, question):
    # DUMMY/TEST MODE:
    # If the user asks for a test or the API key is not set up, act as an AI Agent.
    is_dummy_request = any(k in question.lower() for k in ["dummy", "test", "check", "ping"])
    is_invalid_key = not VIBELETS_API_KEY or VIBELETS_API_KEY == "your-vibelets-api-key"

    if is_dummy_request or is_invalid_key:
        # Try using Gemini if available
        if GEMINI_API_KEY and GEMINI_API_KEY != "your_gemini_api_key_here":
            try:
                genai.configure(api_key=GEMINI_API_KEY)
                # Use 'gemini-2.0-flash' as requested
                model = genai.GenerativeModel('gemini-2.0-flash')
                response = model.generate_content(
                    f"You are the Vibelets AI Bot. Answer this user query concisely: {question}"
                )
                return f"✨ *[Gemini AI]*\n{response.text}"
            except Exception as e:
                # Log the real error to console, but show a nice message to user
                return (
                    f"🤖 *[System Message]*\n"
                    f"I am currently upgrading my brain. 🧠\n"
                    f"Please try again later or contact support."
                )

        # Fallback to static dummy text (only if NO key is present)
        return (
            f"🤖 *[Dummy Agent]*\n"
            f"I received your query: _'{question}'_\n\n"
            f"✅ **System Status:** Operational"
        )
    
    try:
        response = requests.post(
            f"{VIBELETS_BASE_URL}/bot/resolve",
            headers={"Authorization": f"Bearer {VIBELETS_API_KEY}"},
            json={"user_id": user_id, "question": question},
            timeout=10
        )
        response.raise_for_status()
        return response.json().get("answer", "No response found")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Vibelets AI: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def push_notification(payload):
    msg = f"*{payload.title}*\n{payload.summary}"
    
    if payload.platform == "slack":
        # Local import to avoid circular dependency with slack_service
        from services.slack_service import send_message as slack_send_message
        return slack_send_message(payload.channel_id, msg)
    
    return {"status": "failed", "reason": "Unsupported platform"}
