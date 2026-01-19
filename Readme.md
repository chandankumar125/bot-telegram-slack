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


