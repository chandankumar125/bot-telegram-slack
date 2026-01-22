# User Integration Flow

## Authorization Flow (The "Atlassian-like" Experience)

To achieve the flow where a user clicks "Connect Slack" on the Vibelets Dashboard and is securely connected, we use the standard **OAuth 2.0** flow.

### 1. The Setup (Frontend)
On the Vibelets Dashboard (Sidebar -> Integrations), add a "Connect Slack" button.
This button should point to your backend endpoint:

```
https://<YOUR_BOT_DOMAIN>/bot/slack/install?user_id=<CURRENT_USER_ID>
or

<a href="https://api.vibelets.ai/bot/slack/install?user_id=VL_12345">
  Connect Slack
</a>


```

### 2. Redirect to Slack: Backend – Install Endpoint: routes/slack.py
*   The backend redirects the user to `slack.com/oauth/v2/authorize`.
*   The user sees the consent screen: "Vibelets Bot wants to access your workspace..."
*   User clicks "Allow".

### 3. The Callback
*   Slack redirects the user *back* to your backend: `/bot/slack/oauth_callback`.
*   Your backend receives a temporary `code`.
*   Your backend exchanges this `code` for a permanent `access_token` and `bot_user_id`. 

### 4. Linking
*   We extract the `user_id` from the `state` parameter we passed earlier.
*   We link the **Slack Team ID** & **User ID** to the **Vibelets User Account** in the database.
*   We redirect the user back to the Vibelets Dashboard with a generic "Success" message.

### Telegram Connection Flow
1. **Frontend**: Calls `/bot/telegram/connect?user_id=123`.
2. **Backend**: Generates a deep link `https://t.me/MyBot?start=123`.
3. **User**: Clicks link, opens Telegram, taps "Start".
4. **Backend**: Receives `/start 123` via webhook.
5. **Linking**: Maps `telegram_chat_id` to `vibelets_user_id` in `db.json` and replies with success message.

---

## Notification Logic

Once connected, the flow for "AI Insights & Thresholds" works as follows:

1.  **Monitor**: The Vibelets Engine monitors ad campaigns.
2.  **Detect**: When a threshold is breached (e.g., CPA > $50), the system generates an alert.
3.  **Lookup**: The system looks up the connected Slack ID for that user.
4.  **Push**: The system calls `/bot/notify` (which uses `services/vibelets_service.py`).
5.  **Alert**: The user receives a DM or Channel message:
    > 🚨 **CPA Alert**: Your campaign is fatigue. Recommendation: Update creative.

---

## Interactive Query Logic (AI Insights)

Beyond receiving alerts, the user can have a **2-way conversation** to dig deeper into the data.

### 1. User Asks Question
*   **Action**: User replies to the alert or starts a new thread.
*   **Example**: "Why is the CPA high?" or "Show me the creative performance."

### 2. Event Webhook
*   Slack sends the message event to `/bot/slack/events`.
*   **Handler**: `services/slack_service.py` -> `handle_event()`.

### 3. Processing
*   The bot identifies the user (Slack User ID).
*   It checks against special commands (`connect`, `help`).
*   If it's a natural language question, it proceeds to resolution.

### 4. AI Resolution
*   **Function**: `services/vibelets_service.py` -> `resolve_query(user_id, question)`.
*   **API Call**: The bot sends a POST request to the **Vibelets Brain**:
    ```json
    POST https://preprod.vibelets.ai/api/bot/resolve
    {
       "user_id": "U12345",
       "question": "Why is the CPA high?"
    }
    ```
*   **AI Engine**: The Vibelets Brain analyzes the real-time ad data for that user's account.

### 5. Response
*   The AI returns a summarized answer:
    > "The CPA increased because CPM rose by 20% this weekend. However, CTR remains stable."
*   The bot posts this back to the Slack channel via `client.chat_postMessage`.
