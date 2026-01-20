# Vibelets.ai Bot Integration

This service powers the Slack integration for Vibelets.ai.
It allows users to:
1.  **Receive Real-time Insights**: Notifications about ad campaigns.
2.  **Query Data**: Ask natural language questions about performance.
3.  **Connect Accounts**: Link Slack identities to Vibelets accounts.

## Architecture

```
Vibelets.ai Engine
        │
        ▼ (Webhook)
FastAPI Bot Backend  <-- YOU ARE HERE
        │
  ┌─────┴──────┐
  ▼            
Slack App

```

## Features
- **Slack Integration**:
    - **App Mentions**: `@VibeletsBot how is my ad set performing?`
    - **Direct Messages**: Chat privately with the bot.
    - **Notifications**: Receive alerts in specific channels.

## Setup & Configuration

1.  **Environment Variables**:
    Create a `.env` file from `.env.example`:
    ```env
    SLACK_BOT_TOKEN=xoxb-...
    SLACK_SIGNING_SECRET=...
    VIBELETS_API_KEY=...
    VIBELETS_BASE_URL=https://api.vibelets.ai/api
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run Locally**:
    ```bash
    uvicorn main:app --reload --port 8000
    ```

    Expose via Ngrok for Slack development:
    ```bash
    .\ngrok.exe http 8000
    ```

## Production Deployment

1.  **Slack App Configuration**:
    - **Interactivity & Shortcuts**: Request URL: `https://your-domain.com/bot/slack/events`
    - **Event Subscriptions**: Enable Events. Request URL: `https://your-domain.com/bot/slack/events`
        - Subscribe to: `app_mention`, `message.im`
    - **OAuth & Permissions**:
        - Scopes: `chat:write`, `commands`, `app_mentions:read`, `im:history`

2.  **Run with Production Server**:
    Use `gunicorn` with `uvicorn` workers for production stability.
    ```bash
    gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
    ```

## Usage

- **Start**: Type `hi` or `help` to see options.
- **Connect**: Type `connect` to get a link to link your Vibelets account.
- **Query**: "What is my CPA for campaign X?"

1. The Handshake (OAuth)
Request: Your backend sends your client_id, client_secret, and the temporary code (received from the browser redirect) to Slack's API https://slack.com/api/oauth.v2.access.
Response: Slack verifies these and returns a JSON payload containing the access keys.

2. The Data Fetched (Response from Slack)
From that response, your code extracts these 5 specific pieces of information:

Data Field	Description
access_token	The Key. This is the permanent password your bot uses to post messages, read channels, etc.
team_id	The unique ID of the Slack Workspace (e.g., T0123456).
team_name	The human-readable name of the workspace (e.g., "Adsparkx").
bot_user_id	The User ID of your bot inside that workspace (e.g., U0987654). This helps the bot know when it is being mentioned versus someone else.
authed_user	(Currently unused by your code, but available). The ID of the specific user who clicked "Install".

3. The Data Stored (Your Database)
Your 
utils/db.py
 saves this data into db.json in two places:

Users Table (db["users"]):
Links your local user (VL_TEST_USER_001) to the Slack Team ID (Txxxx).
Stores connected: True and team_name.
Teams Table (db["teams"]):
Stores the sensitive access_token linked to the team_id.
This is separated so multiple users from the same company can use the same bot connection without needing multiple tokens.