# Vibelets.ai Bot Integration (FastAPI + Slack)

This service powers the production-grade Slack integration for **Vibelets.ai**. It connects users' Slack workspaces to the Vibelets dashboard, enabling real-time ad insights, natural language queries via AI, and proactive notifications.

## 🚀 Features

### Core Functionality
*   **OAuth 2.0 Authentication**: Secure "Add to Slack" flow with state validation.
*   **Real-time Messaging**: Responds to Direct Messages (DMs) and `@App` mentions.
*   **Proactive Notifications**: Send alerts to specific users or channels programmaticallly.
*   **Multi-Tenancy**: Support for multiple Slack workspaces (Teams) and multiple users per team.

### Intelligent & User-Centric
*   **AI-Powered Responses**: Integrated with `Google Gemini` (`gemini-2.0-flash`) or `gemini-pro` for handling natural language queries when specific data isn't available.
*   **Smart Feedback**:
    *   **Welcome Message**: Immediately greets users upon successful connection.
    *   **Goodbye Message**: Notifies users when they disconnect from the dashboard.
    *   **"Not Connected" Guard**: Polite warning if a disconnected user tries to chat.

### Robustness & Security
*   **Token Rotation**: Automatically handles Slack's rotating tokens (refresh tokens) to prevent expiry after 12 hours.
*   **Signature Verification**: Verifies `X-Slack-Signature` on all incoming events.
*   **Database Normalization**: Separates User identity from Team credentials in `db.json`.

---

## 🛠️ Architecture

```mermaid
graph TD
    User((User)) -->|ChatMessage| Slack[Slack Platform]
    Slack -->|Webhook (Event)| Ngrok[Ngrok Tunnel]
    Ngrok -->|HTTPS POST| API[FastAPI Backend]
    
    subgraph "Backend System"
        API -->|Verify Signature| Auth[Security Check]
        Auth -->|Lookup User| DB[(db.json)]
        DB -->|Get Token| API
        
        API -->|Make Decision| Logic{Handle Event}
        Logic -->|AI Query| Gemini[Google Gemini API]
        Logic -->|Data Query| Vibelets[Vibelets Engine]
        
        Logic -->|Reply| Slack
    end
```

---

## ⚙️ Setup & Configuration

### 1. Prerequisites
*   Python 3.9+
*   A Slack App created at [api.slack.com](https://api.slack.com/apps)
*   Ngrok (for local development)

### 2. Environment Variables
Create a `.env` file in the root directory:

```env
# Slack Credentials
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_CLIENT_ID=your-client-id
SLACK_CLIENT_SECRET=your-client-secret
SLACK_REDIRECT_URI=https://your-ngrok-domain.ngrok-free.dev/bot/slack/oauth_callback

# App Config
DASHBOARD_URL=http://localhost:8000/dashboard/
VIBELETS_API_KEY=your-vibelets-key
VIBELETS_BASE_URL=https://api.vibelets.ai/api

# AI Config
GEMINI_API_KEY=your-gemini-api-key
```

### 3. Installation
```bash
# Create Virtual Environment (Optional but recommended)
python -m venv .venv
.\.venv\Scripts\Activate  # Windows

# Install Requirements
pip install -r requirements.txt
```

### 4. Running the Server
```bash
# Start FastAPI with Hot Reload
uvicorn main:app --reload --port 8000

# Start Ngrok (In a separate terminal)
.\ngrok.exe http 8000
```
> **Important**: Update `SLACK_REDIRECT_URI` in `.env` and in your Slack App Dashboard > *OAuth & Permissions* > *Redirect URLs* whenever your Ngrok URL changes.

---

## 📚 Data Structure (`db.json`)

The system uses a flat-file JSON database for simplicity, normalized into two tables:

### 1. Users Table (`users`)
Maps a Vibelets User ID (`VL_TEST_USER_001`) to their Slack identity.
```json
"VL_TEST_USER_001": {
    "slack": {
        "connected": true,
        "team_id": "T0A8NCYDA10",      // Link to Teams table
        "slack_user_id": "U0A8LC3ELP8" // The User's ID in Slack
    }
}
```

### 2. Teams Table (`teams`)
Stores the credentials for the Workspace. Multiple users can belong to one team.
```json
"T0A8NCYDA10": {
    "team_name": "Adsparkx",
    "access_token": "xoxb-...",      // The active Access Token
    "refresh_token": "xoxe-...",     // Used to get new access tokens
    "expires_at": 1731500000         // Timestamp when token expires
}
```

---

## 🔑 Key Features Explained

### Slack Token Rotation
The bot supports **Token Rotation**. If Slack issues a token that expires (e.g., every 12 hours), the `services/slack_service.py` module automatically checks expiry before every request.
1.  **Check**: Is `expires_at` within the next 5 minutes?
2.  **Refresh**: If yes, calls `oauth.v2.access` with `refresh_token`.
3.  **Update**: Saves new keys to `db.json`.
4.  **Act**: Proceed with the API call using the fresh token.

### Disconnect Flow
When a user clicks **Disconnect** on the dashboard:
1.  We lookup their Slack details.
2.  We send a **"Goodbye" message** to their Slack DM (`client.chat_postMessage`).
3.  We **remove** their record from `db["users"]`.
4.  **Result**: If they message again, the bot doesn't know them and replies "Please Connect".

### Notifications
You can trigger alerts from anywhere in the backend using the helper:
```python
from services.slack_service import send_notification

send_notification(
    team_id="T0A8...", 
    channel_id="U0A8...", 
    text="🚀 Campaign limit reached!"
)
```

**Test Script**: Run `python send_test_notification.py` to verify this system.

---

## 🤖 AI Integration
The bot uses **Google Gemini** as the Fallback Agent.
*   **File**: `services/vibelets_service.py`
*   **Logic**: If the text matches a hardcoded command (e.g., "connect"), specific logic runs. Otherwise, the query is passed to `gemini-2.0-flash`.
*   **Error Handling**: If Gemini is down or misconfigured, it returns a polite "Upgrading my brain" message instead of crashing.

---

## 🐛 Troubleshooting

*   **"Account Not Connected" Error**:
    *   Ensure you clicked "Connect Slack" on the dashboard.
    *   Ensure the `slack_user_id` in `db.json` matches the user sending the message.
*   **Bot doesn't reply**:
    *   Check `ngrok` terminal for `200 OK` on `/bot/slack/events`.
    *   If `404` or `500`, check backend logs.
    *   Ensure the bot (App) is invited to the channel (`/invite @Demo App`).
*   **Changes not reflecting?**:
    *   Restart `uvicorn` if you changed `.env` or python structure.
    *   We use `reload=True`, so code changes should auto-load.