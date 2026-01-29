from services.vibelets_service import resolve_query
from utils.db import get_vibelets_user_by_whatsapp_id, save_whatsapp_connection, disconnect_whatsapp_connection
from helpers.whatsapp_api import send_whatsapp_message
import logging


# Configure logging
logger = logging.getLogger(__name__)

def send_message(to_number: str, text: str):
    """
    Sends a text message to a WhatsApp user via Graph API.
    """
    try:
        response_data = send_whatsapp_message(to_number, text)
        return {"ok": True, "data": response_data}
            
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return {"ok": False, "error": str(e)}

from schemas.whatsapp import WhatsAppWebhookPayload

def handle_incoming_message(payload: WhatsAppWebhookPayload):
    """
    Process incoming WhatsApp webhook payload.
    """
    try:
        # Pydantic models ensure these exist, but lists could still be empty
        if not payload.entry:
            return {"ok": True, "message": "No entries"}
            
        entry = payload.entry[0]
        
        if not entry.changes:
            return {"ok": True, "message": "No changes"}

        changes = entry.changes[0]
        value = changes.value
        
        # Check if it is a message or just a status update
        if not value.messages:
            return {"ok": True, "message": "No messages found (status update)"}
            
        message = value.messages[0]
        from_number = message.from_  # using the alias we defined
        
        # Get Contact Name if available
        contact_name = "User"
        if value.contacts:
            contact = value.contacts[0]
            if contact.profile and contact.profile.name:
                contact_name = contact.profile.name

        if message.type != "text" or not message.text:
            send_message(from_number, "Sorry, I currently only understand text messages.")
            return {"ok": True}
        
        text = message.text.body
        logger.info(f"Received WhatsApp message from {from_number} ({contact_name}): {text}")
        
        # --- Logic Handling ---
        
        # 1. Check Connection
        vibelets_user_id = get_vibelets_user_by_whatsapp_id(from_number)
        
        # 2. Handle Connect Command
        if text.lower().startswith("connect"):
            parts = text.split()
            if len(parts) > 1:
                target_user_id = parts[1]
                import json
                print("\n" + "="*50)
                print(f"STAGE 2: Received WhatsApp Connection Command")
                print("-" * 50)
                print(json.dumps({
                    "Command": "connect",
                    "User ID (Vibelets)": target_user_id,
                    "WhatsApp Number": from_number,
                    "Contact Name": contact_name
                }, indent=2))
                print("="*50 + "\n")

                save_whatsapp_connection(target_user_id, from_number, from_number, contact_name)
                
                msg = (
                    f"✅ *Connected Successfully!*\n"
                    f"Hello {contact_name}, your WhatsApp is now linked to Vibelets account `{target_user_id}`.\n"
                    f"You can now ask me questions about your ad campaigns."
                )
                send_message(from_number, msg)
                return {"ok": True}
            else:
                 msg = (
                    f"⚠️ *Connection Failed*\n"
                    f"Please provide your Vibelets User ID.\n"
                    f"Usage: `Connect <YOUR_USER_ID>`"
                )
                 send_message(from_number, msg)
                 return {"ok": True}

        if not vibelets_user_id:
            msg = (
                f"👋 *Welcome to Vibelets Bot (WhatsApp)*\n"
                f"You are not connected yet.\n\n"
                f"To connect, please reply with:\n`Connect <YOUR_USER_ID>`"
            )
            send_message(from_number, msg)
            return {"ok": True}

        # 3. Handle Disconnect
        if text.lower().strip() == "disconnect":
             disconnect_whatsapp_connection(vibelets_user_id)
             send_message(from_number, "⚠️ You have been disconnected.")
             return {"ok": True}

        # 4. Handle Help/Hello
        if text.lower().strip() in ["hi", "hello", "help", "start"]:
            msg = (
                f"👋 *Hello {contact_name}!*\n"
                f"I'm ready to help you with your ad campaigns.\n\n"
                f"• Ask me questions like _'How is my campaign performing?'_\n"
                f"• Type `Disconnect` to unlink your account."
            )
            send_message(from_number, msg)
            return {"ok": True}

        # 5. Handle AI Query
        reply = resolve_query(vibelets_user_id, text)
        send_message(from_number, reply)
        
        return {"ok": True}

    except Exception as e:
        import traceback
        traceback.print_exc()
        logger.error(f"Error processing WhatsApp webhook: {e}")
        return {"ok": False, "error": str(e)}
