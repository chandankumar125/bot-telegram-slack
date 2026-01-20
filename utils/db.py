import json
import os
from typing import Dict, Optional

DB_FILE = "db.json"

def _load_db() -> Dict:
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"users": {}}

def _save_db(data: Dict):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

import time

def save_slack_connection(user_id: str, team_id: str, team_name: str, access_token: str, bot_user_id: str, slack_user_id: str = None, refresh_token: str = None, expires_in: int = None):
    db = _load_db()
    
    # 1. Save User mapping
    if "users" not in db:
        db["users"] = {}
    
    db["users"][user_id] = {
        "slack": {
            "connected": True,
            "team_id": team_id,
            "team_name": team_name,
            "bot_user_id": bot_user_id,
            "slack_user_id": slack_user_id
        }
    }

    # 2. Save Team Token independently
    if "teams" not in db:
        db["teams"] = {}
    
    # Calculate expiry if provided
    expires_at = None
    if expires_in:
        expires_at = int(time.time()) + expires_in

    # Store everything
    db["teams"][team_id] = {
        "access_token": access_token,
        "team_name": team_name,
        "bot_user_id": bot_user_id,
        "refresh_token": refresh_token,
        "expires_at": expires_at
    }
    
    _save_db(db)

def update_team_token(team_id: str, access_token: str, refresh_token: str, expires_in: int):
    """
    Updates the token after a refresh.
    """
    db = _load_db()
    if "teams" in db and team_id in db["teams"]:
        expires_at = int(time.time()) + expires_in
        
        db["teams"][team_id]["access_token"] = access_token
        db["teams"][team_id]["refresh_token"] = refresh_token
        db["teams"][team_id]["expires_at"] = expires_at
        _save_db(db)
        return True
    return False

def get_team_data(team_id: str) -> Optional[Dict]:
    """Retrieve full team data including refresh tokens."""
    db = _load_db()
    return db.get("teams", {}).get(team_id)

def get_vibelets_user_by_slack_id(slack_user_id: str):
    db = _load_db()
    if "users" not in db:
        return None
    
    for uid, data in db["users"].items():
        if "slack" in data:
            # Check if this user has the matching slack_user_id
            # OR if it's the legacy setup where we didn't save it (fallback logic might be needed)
            if data["slack"].get("slack_user_id") == slack_user_id:
                return uid
    return None

def get_slack_connection(user_id: str) -> Optional[Dict]:
    db = _load_db()
    user_data = db.get("users", {}).get(user_id, {})
    return user_data.get("slack")

def get_team_token(team_id: str) -> Optional[str]:
    db = _load_db()
    team_data = db.get("teams", {}).get(team_id, {})
    return team_data.get("access_token")

def disconnect_slack_connection(user_id: str):
    db = _load_db()
    
    # 1. Check if user exists and has slack data
    if "users" in db and user_id in db["users"] and "slack" in db["users"][user_id]:
        
        # Get the team_id specifically associated with this user
        team_id = db["users"][user_id]["slack"].get("team_id")
        
        # 2. Remove User Mapping
        del db["users"][user_id]["slack"]
        
        # NOTE: We do NOT remove the Team Token from db["teams"] anymore.
        # This allows the bot to still "speak" (using the team token) to tell the user 
        # "Please connect your account" even if they are disconnected in our system.
            
        _save_db(db)
        return True
        
    return False
