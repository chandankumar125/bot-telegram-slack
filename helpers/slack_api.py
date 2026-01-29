"""
Slack API Integration Module

This module handles all Slack API interactions including:
- User authorization (OAuth): authorize_slack_user
- Token refreshing: refresh_slack_token
- Webhook signature verification: verify_slack_request
- Message publishing: publish_slack_message
- User information retrieval: get_slack_user_info

"""

import os
import time
import hmac
import hashlib
import requests
import json
from typing import Dict, Any, Optional

# Get configuration from environment
SLACK_CLIENT_ID = os.getenv('SLACK_CLIENT_ID')
SLACK_CLIENT_SECRET = os.getenv('SLACK_CLIENT_SECRET')
SLACK_SIGNING_SECRET = os.getenv('SLACK_SIGNING_SECRET')
SLACK_API_URL = "https://slack.com/api" 

def authorize_slack_user(
    code: str, 
    redirect_uri: str, 
    client_id: str = None, 
    client_secret: str = None
) -> Dict[str, Any]:
    """
    Exchange an authorization code for an access token.
    
    Args:
        code (str): The authorization code received from Slack.
        redirect_uri (str): The redirect URI used in the initial request.
        client_id (str): Slack Client ID (optional, uses env var if not provided).
        client_secret (str): Slack Client Secret (optional, uses env var if not provided).
        
    Returns:
        Dict[str, Any]: The JSON response from Slack containing the access token.
        
    Raises:
        Exception: If the request fails or the response contains an error.
    """
    c_id = client_id or SLACK_CLIENT_ID
    c_secret = client_secret or SLACK_CLIENT_SECRET
    
    if not c_id or not c_secret:
        raise Exception("Slack Client ID and Secret are required.")
        
    try:
        url = f"{SLACK_API_URL}/oauth.v2.access"
        data = {
            "client_id": c_id,
            "client_secret": c_secret,
            "code": code,
            "redirect_uri": redirect_uri
        }
        
        response = requests.post(url, data=data)
        print(f"DEBUG: Slack OAuth Response: {response.text}")
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data.get("ok"):
            raise Exception(f"Slack OAuth failed: {response_data.get('error')}")
            
        return response_data
        
    except requests.RequestException as e:
        raise Exception(f"Failed to authorize Slack user: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response from Slack: {str(e)}")


def refresh_slack_token(
    refresh_token: str, 
    client_id: str = None, 
    client_secret: str = None
) -> Dict[str, Any]:
    """
    TWO modes in Slack:  
    Mode 1: Token rotation DISABLED- Access token: xoxb- / xoxp- ❌ No expiry ❌ No refresh token ❌ No refresh API, Token lives until revoked or app uninstalled, No refresh ever happens.  
    Mode 2: Token rotation ENABLED- Access token Expires every 12 hours, Refresh token-✅ Issued, Refresh token usage🔁 Single-use,  Access token prefix-  xoxe. (important!), Refresh token prefix-  xoxe-, Auto revoke- Old refresh token revoked after use
    
    """
    """
    Refresh an expired Slack access token.
    
    Args:
        refresh_token (str): The refresh token.
        client_id (str): Slack Client ID (optional, uses env var if not provided).
        client_secret (str): Slack Client Secret (optional, uses env var if not provided).
        
    Returns:
        Dict[str, Any]: The JSON response from Slack  the new access token.
        
    Raises:
        Exception: If the token refresh fails.
    """
    c_id = client_id or SLACK_CLIENT_ID
    c_secret = client_secret or SLACK_CLIENT_SECRET
    
    if not c_id or not c_secret:
        raise Exception("Slack Client ID and Secret are required for token refresh.")
        
    try:
        url = f"{SLACK_API_URL}/oauth.v2.access"
        data = {
            "client_id": c_id,
            "client_secret": c_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        
        
        print("\n" + "="*50)
        print("DEBUG: Refreshing Slack Token")
        print("-" * 50)
        print(json.dumps({
            "URL": url,
            "Refresh Token Prefix": refresh_token[:10] + "..."
        }, indent=2))

        response = requests.post(url, data=data)
        
        try:
            resp_json = response.json()
        except:
            resp_json = response.text

        print("DEBUG: Slack Refresh Response:")
        print(json.dumps(resp_json, indent=2))
        print("="*50 + "\n")
        
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data.get("ok"):
            raise Exception(f"Failed to refresh Slack token: {response_data.get('error')}")
            
        return response_data
        
    except requests.RequestException as e:
        raise Exception(f"Error during Slack token refresh: {str(e)}")


def verify_slack_request(
    body: str, 
    timestamp: str, 
    signature: str, 
    signing_secret: str = None
) -> bool:
    """
    Verify the signature of a request from Slack.
    
    Args:
        body (str): The raw body of the request.
        timestamp (str): The X-Slack-Request-Timestamp header.
        signature (str): The X-Slack-Signature header.
        signing_secret (str): Slack Signing Secret (optional, uses env var if not provided).
        
    Returns:
        bool: True if the signature is valid, False otherwise.
        
    Raises:
        Exception: If the signing secret is missing.
    """
    secret = signing_secret or SLACK_SIGNING_SECRET
    if not secret:
        raise Exception("Slack Signing Secret is required for verification.")
        
    # Check for replay attacks (timestamp older than 5 minutes)
    if abs(time.time() - int(timestamp)) > 60 * 5:
        return False
        
    basestring = f"v0:{timestamp}:{body}"
    
    # Create the HMAC signature using SHA256
    calculated_signature = "v0=" + hmac.new(
        secret.encode(), 
        basestring.encode(), 
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_signature, signature)


def publish_slack_message(
    token: str, 
    channel_id: str, 
    text: str, 
    blocks: Optional[list] = None
) -> Dict[str, Any]:
    """
    Publish a message to a Slack channel.
    
    Args:
        token (str): Slack `Access Token (Bot User OAuth Token).
        channel_id (str): The ID of the channel to post to.
        text (str): The text content of the message.
        blocks (list): Optional JSON blocks for rich formatting.
        
    Returns:
        Dict[str, Any]: The JSON response from Slack.
        
    Raises:
        Exception: If the message sending fails.
    """
    try:
        url = f"{SLACK_API_URL}/chat.postMessage"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "channel": channel_id,
            "text": text
        }
        
        if blocks:
            payload["blocks"] = blocks
            
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data.get("ok"):
            raise Exception(f"Failed to publish message: {response_data.get('error')}")
            
        return response_data
        
    except requests.RequestException as e:
        raise Exception(f"Error publishing Slack message: {str(e)}")


def get_slack_user_info(token: str, user_id: str) -> Dict[str, Any]:
    """
    Retrieve information about a Slack user.
    
    Args:
        token (str): Slack Access Token.
        user_id (str): The Slack User ID.
        
    Returns:
        Dict[str, Any]: The user profile information.
        
    Raises:
        Exception: If retrieval fails.
    """
    try:
        url = f"{SLACK_API_URL}/users.info"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        params = {
            "user": user_id
        }
        
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        
        response_data = response.json()
        
        if not response_data.get("ok"):
            raise Exception(f"Failed to get user info: {response_data.get('error')}")
            
        return response_data
        
    except requests.RequestException as e:
        raise Exception(f"Error fetching Slack user info: {str(e)}")
