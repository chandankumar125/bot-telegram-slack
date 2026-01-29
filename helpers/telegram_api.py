"""
Telegram API Integration Module

This module handles Telegram Bot API interactions including:
- Sending messages
- Setting webhooks
- Retrieving bot information
"""

import os
import requests
import json
from typing import Dict, Any, Optional

# Get configuration from environment
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_API_BASE = "https://api.telegram.org/bot"

def _get_base_url(token: str = None) -> str:
    """Helper to construct the base URL with token."""
    t = token or TELEGRAM_BOT_TOKEN
    if not t:
        raise Exception("Telegram Bot Token is required.")
    return f"{TELEGRAM_API_BASE}{t}"

# Sends a message to a Telegram chat.
def send_telegram_message(
    chat_id: str, 
    text: str, 
    token: str = None, 
    parse_mode: str = "Markdown"
) -> Dict[str, Any]:
    """
    Send a message to a Telegram chat.
    
    Args:
        chat_id (str): Unique identifier for the target chat or username.
        text (str): Text of the message to be sent.
        token (str): Bot Token (optional, uses env var if not provided).
        parse_mode (str): Mode for parsing entities in the message text ('Markdown', 'HTML', or None).
        
    Returns:
        Dict[str, Any]: The JSON response from Telegram.
        
    Raises:
        Exception: If the request fails.
    """
    try:
        base_url = _get_base_url(token)
        url = f"{base_url}/sendMessage"
        
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        
        if parse_mode:
            payload["parse_mode"] = parse_mode
            
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        print("\n" + "="*50)
        print(f"DEBUG: Telegram API Response ({url}):")
        print("-" * 50)
        print(json.dumps(response_data, indent=2))
        print("="*50 + "\n")
        
        if not response_data.get("ok"):
            raise Exception(f"Failed to send Telegram message: {response_data.get('description')}")
            
        return response_data
        
    except requests.RequestException as e:
        # Fallback for Markdown errors? The service file had a retry logic.
        # But this is a raw API helper, so we perhaps should just raise or let the caller handle retry.
        # I will propagate the error.
        raise Exception(f"Error sending Telegram message: {str(e)}")

# Verifies bot identity.
def get_telegram_me(token: str = None) -> Dict[str, Any]:
    """
    A simple method for testing your bot's authentication token.
    
    Args:
        token (str): Bot Token (optional).
        
    Returns:
        Dict[str, Any]: Basic information about the bot in form of a User object.
    """
    try:
        base_url = _get_base_url(token)
        url = f"{base_url}/getMe"
        
        response = requests.get(url)
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data.get("ok"):
             raise Exception(f"Failed to get bot info: {response_data.get('description')}")
             
        return response_data
        
    except requests.RequestException as e:
        raise Exception(f"Error fetching Telegram bot info: {str(e)}")

# Sets up a webhook to receive updates from Telegram.
def set_telegram_webhook(url: str, token: str = None, secret_token: str = None) -> Dict[str, Any]:
    """
    Specify a URL and receive incoming updates via an outgoing webhook.
    
    Args:
        url (str): HTTPS URL to send updates to.
        token (str): Bot Token (optional).
        secret_token (str): A secret token to be sent in a header “X-Telegram-Bot-Api-Secret-Token” in every webhook request.
        
    Returns:
        Dict[str, Any]: The JSON response from Telegram.
    """
    try:
        base_url = _get_base_url(token)
        endpoint = f"{base_url}/setWebhook"
        
        payload = {
            "url": url
        }
        
        if secret_token:
            payload["secret_token"] = secret_token
            
        response = requests.post(endpoint, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data.get("ok"):
             raise Exception(f"Failed to set webhook: {response_data.get('description')}")
             
        return response_data
        
    except requests.RequestException as e:
        raise Exception(f"Error setting Telegram webhook: {str(e)}")
