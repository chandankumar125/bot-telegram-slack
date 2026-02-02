# Vibelets Bot API Documentation

This document lists all available API endpoints, their purposes, methods, payloads (inputs), and expected responses. Use this as a reference for Postman testing.

## Base URL
`http://localhost:8000` (or your ngrok URL)

---

## 1. Authentication (JWT)
**Note:** Endpoints marked with 🔒 **Strict Auth** require the following header:
`Authorization: Bearer <your_jwt_token>`

For testing, generate a JWT with payload `{"sub": "1"}` (or your desired user ID) signed with your `JWT_SECRET` (default: `your-secret-key-12345`).

---

## 2. Slack Integration

### A. Install (Connect)
**Endpoint:** `GET /bot/slack/install`
*   **Description:** Initiates the OAuth flow. Redirects the browser to Slack.
*   **Query Params:**
    *   `user_id` (string): The Vibelets User ID connecting (e.g., `1`).
*   **Curl:**
    ```bash
    curl -I "http://localhost:8000/bot/slack/install?user_id=1"
    ```
*   **Response:** `307 Temporary Redirect` -> Slack.com

### B. OAuth Callback (Internal)
**Endpoint:** `GET /bot/slack/oauth_callback`
*   **Description:** Slack redirects back here with a code. Backend exchanges code for token.
*   **Query Params:** `code`, `state` (Passed by Slack).
*   **Response:** `307 Temporary Redirect` -> Dashboard.

### C. Connection Status 🔒
**Endpoint:** `GET /bot/slack/status`
*   **Description:** Checks if the authenticated user is connected to Slack.
*   **Headers:** `Authorization: Bearer <token>`
*   **Curl:**
    ```bash
    curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/bot/slack/status
    ```
*   **Response (Connected):**
    ```json
    {
        "connected": true,
        "team_name": "Adsparkx",
        "team_id": "T123456",
        "slack_user_id": "U123456",
        "email": "user@example.com",
        "bot_user_id": "B987654",
        "access_token": "xoxb-..."
    }
    ```
*   **Response (Not Connected):**
    ```json
    { "connected": false }
    ```

### D. Disconnect 🔒
**Endpoint:** `POST /bot/slack/disconnect`
*   **Description:** Disconnects the authenticated user from Slack.
*   **Headers:** `Authorization: Bearer <token>`
*   **Curl:**
    ```bash
    curl -X POST -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/bot/slack/disconnect
    ```
*   **Response:**
    ```json
    { "ok": true, "message": "Disconnected successfully" }
    ```

### E. Webhook (Events)
**Endpoint:** `POST /bot/slack/events`
*   **Description:** Receives real-time events from Slack (messages, mentions).
*   **Headers:** `X-Slack-Signature`, `X-Slack-Request-Timestamp` (Sent by Slack).
*   **Curl (Simulated):**
    ```bash
    curl -X POST http://localhost:8000/bot/slack/events \
    -H "Content-Type: application/json" \
    -d '{ "type": "url_verification", "challenge": "test" }'
    ```
*   **Payload (Example - Message):**
    ```json
    {
        "token": "...",
        "team_id": "T123456",
        "api_app_id": "A123456",
        "event": {
            "type": "message",
            "text": "How are my ads?",
            "user": "U123456",
            "channel": "C123456",
            "ts": "161..."
        },
        "type": "event_callback"
    }
    ```
*   **Response:** `{ "ok": true }` (or `challenge` string if verifying).

---

## 3. Telegram Integration

### A. Get Connect Link 🔒
**Endpoint:** `GET /bot/telegram/connect`
*   **Description:** Returns a deep link to start the Telegram bot.
*   **Headers:** `Authorization: Bearer <token>`
*   **Curl:**
    ```bash
    curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/bot/telegram/connect
    ```
*   **Response:**
    ```json
    { "link": "https://t.me/Vibelets_Bot?start=1" }
    ```

### B. Webhook
**Endpoint:** `POST /bot/telegram/webhook`
*   **Description:** Receives updates from Telegram.
*   **Curl:**
    ```bash
    curl -X POST http://localhost:8000/bot/telegram/webhook \
    -H "Content-Type: application/json" \
    -d '{ "update_id": 1, "message": { "text": "Hello", "chat": { "id": 123 }, "from": { "id": 123 } } }'
    ```
*   **Payload:** Standard Telegram Update JSON.
*   **Response:** `{ "ok": true }`

### C. Status 🔒
**Endpoint:** `GET /bot/telegram/status`
*   **Description:** Check connection status.
*   **Headers:** `Authorization: Bearer <token>`
*   **Curl:**
    ```bash
    curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/bot/telegram/status
    ```
*   **Response:** `{ "connected": true, "username": "kartik" }`

### D. Disconnect 🔒
**Endpoint:** `POST /bot/telegram/disconnect`
*   **Description:** Disconnects the user.
*   **Headers:** `Authorization: Bearer <token>`
*   **Curl:**
    ```bash
    curl -X POST -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/bot/telegram/disconnect
    ```
*   **Response:** `{ "ok": true }`

---

## 4. WhatsApp Integration

### A. Get Connect Link 🔒
**Endpoint:** `GET /bot/whatsapp/connect`
*   **Description:** Returns deep link to WhatsApp.
*   **Headers:** `Authorization: Bearer <token>`
*   **Curl:**
    ```bash
    curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/bot/whatsapp/connect
    ```
*   **Response:** `{ "link": "https://wa.me/1555023...?text=Connect 1" }`

### B. Webhook Verification
**Endpoint:** `GET /bot/whatsapp/webhook`
*   **Query Params:** `hub.mode`, `hub.verify_token`, `hub.challenge`.
*   **Curl:**
    ```bash
    curl "http://localhost:8000/bot/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_VERIFY_TOKEN&hub.challenge=123"
    ```
*   **Response:** Returns `hub.challenge` integer.

### C. Webhook (Messages)
**Endpoint:** `POST /bot/whatsapp/webhook`
*   **Description:** Receives messages from WhatsApp Cloud API.
*   **Curl:**
    ```bash
    curl -X POST http://localhost:8000/bot/whatsapp/webhook \
    -H "Content-Type: application/json" \
    -d '{ "object": "whatsapp_business_account", "entry": [] }'
    ```
*   **Response:** `{ "status": "ok" }`

### D. Status 🔒
**Endpoint:** `GET /bot/whatsapp/status`
*   **Description:** Check status.
*   **Headers:** `Authorization: Bearer <token>`
*   **Curl:**
    ```bash`
    curl -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/bot/whatsapp/status
    ```
*   **Response:**
    ```json
    { "connected": true, "whatsapp_id": "91999...", "name": "Kartik" }
    ```

### E. Disconnect 🔒
**Endpoint:** `POST /bot/whatsapp/disconnect`
*   **Description:** Disconnects user.
*   **Headers:** `Authorization: Bearer <token>`
*   **Curl:**
    ```bash
    curl -X POST -H "Authorization: Bearer YOUR_TOKEN_HERE" http://localhost:8000/bot/whatsapp/disconnect
    ```
*   **Response:**
    ```json
    { "ok": true, "message": "Disconnected successfully" }
    ```

---

## 5. Notifications (Push)

### Send Notification
**Endpoint:** `POST /bot/notify`
*   **Description:** Sends a proactive notification to a user on all connected platforms.
*   **Curl:**
    ```bash
    curl -X POST http://localhost:8000/bot/notify \
    -H "Content-Type: application/json" \
    -d '{
      "title": "Campaign Alert",
      "summary": "Your ROAS dropped by 10%.",
      "platform": "all",
      "user_id": "1",
      "priority": "high",
      "metadata": { "campaign_id": "123" }
    }'
    ```
*   **Response:**
    ```json
    {
        "status": "success",
        "results": {
            "slack": "sent",
            "telegram": "failed: user not connected"
        }
    }
    ```

---

## 6. General (Health)
**Endpoint:** `GET /health`
*   **Curl:**
    ```bash
    curl http://localhost:8000/health
    ```
*   **Response:** `{ "status": "ok" }`
