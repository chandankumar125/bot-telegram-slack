"""
WhatsApp API Integration Module

This module handles WhatsApp Cloud API interactions including:
- Sending messages: send_whatsapp_message
- Webhook signature verification: verify_whatsapp_signature
"""

import os
import hmac
import hashlib
import requests
import json
import re
from typing import Dict, Any, Optional

# Get configuration from environment
WHATSAPP_ACCESS_TOKEN = os.getenv('WHATSAPP_ACCESS_TOKEN')
WHATSAPP_PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_NUMBER_ID')
WHATSAPP_APP_SECRET = os.getenv('WHATSAPP_APP_SECRET')
WHATSAPP_API_VERSION = "v17.0"

def send_whatsapp_message(
    to_number: str, 
    text: str, 
    phone_number_id: str = None, 
    access_token: str = None
) -> Dict[str, Any]:
    """
    Send a text message to a WhatsApp user.
    
    Args:
        to_number (str): The recipient's phone number.
        text (str): The body text of the message.
        phone_number_id (str): The sending phone number ID (optional, uses env var).
        access_token (str): The access token (optional, uses env var).
        
    Returns:
        Dict[str, Any]: The JSON response from WhatsApp.
        
    Raises:
        Exception: If the request fails.
    """
    p_id = phone_number_id or WHATSAPP_PHONE_NUMBER_ID
    token = access_token or WHATSAPP_ACCESS_TOKEN
    
    if not p_id or not token:
        raise Exception("WhatsApp Phone Number ID and Access Token are required.")
        
    try:
        url = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/{p_id}/messages"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": to_number,
            "type": "text",
            "text": {"body": text}
        }
        
        response = requests.post(url, headers=headers, json=payload)
        # Note: WhatsApp sometimes returns errors in 200 OK responses or 400s, so we check content too.
        
        if response.status_code != 200:
             # Try to parse error
             try:
                 err_data = response.json()
                 raise Exception(f"WhatsApp API Error: {err_data}")
             except json.JSONDecodeError:
                 response.raise_for_status()
        
        return response.json()
        
    except requests.RequestException as e:
        raise Exception(f"Failed to send WhatsApp message: {str(e)}")


def verify_whatsapp_signature(
    body: str, 
    signature: str, 
    app_secret: str = None
) -> bool:
    """
    Verifies the X-Hub-Signature-256 header from Meta/WhatsApp.
    
    Args:
        body (str): The raw request body.
        signature (str): The signature header value (format: sha256=<hash>).
        app_secret (str): The App Secret (optional, uses env var).
        
    Returns:
        bool: True if signature is valid.
        
    Raises:
         Exception: If app secret is missing.
    """
    secret = app_secret or WHATSAPP_APP_SECRET
    if not secret:
        raise Exception("WhatsApp App Secret is required for verification.")
        
    if not signature.startswith("sha256="):
        return False
        
    expected_hash = "sha256=" + hmac.new(
        secret.encode(), 
        body.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected_hash, signature)


def format_for_whatsapp(text: str) -> str:
    """
    Converts standard Markdown to WhatsApp formatting.
    Fetch logic from python-whatsapp-bot/app/utils/whatsapp_utils.py.
    """
    if not text:
        return ""
        
    # Remove brackets like 【...】
    pattern = r"\【.*?\】"
    text = re.sub(pattern, "", text).strip()

    # Convert **bold** to *bold*
    # Pattern to find double asterisks including the word(s) in between
    pattern = r"\*\*(.*?)\*\*"
    replacement = r"*\1*"
    text = re.sub(pattern, replacement, text)
    
    # You might add more conversions here if needed (e.g., _italic_)
    
    return text

