# Telegram Integration Data Flow: "Connect to Telegram"

This document outlines the data flow and technical steps for connecting a user's Vibelets account to the Telegram bot.

## Overview

The integration uses Telegram's **Deep Linking** mechanism to securely pass the Vibelets `user_id` to the bot during the initial interaction. This creates a binding between the Vibelets user and their Telegram Chat ID.

## Data Flow Diagram

1.  **User** clicks "Connect Telegram" on Dashboard.
2.  **Backend** generates a deep link containing the `user_id`.
3.  **User** is redirected to Telegram and clicks "Start".
4.  **Telegram** sends a Webhook event to the Backend.
5.  **Backend** extracts `user_id` and `chat_id`.
6.  **Database** stores the connection.
7.  **Bot** sends a confirmation message.

---

## Detailed Step-by-Step Flow

### 1. Link Generation (Frontend -> Backend)

*   **Action**: User clicks the "Connect Telegram" button on the Vibelets Dashboard.
*   **Request**: `GET /bot/telegram/connect?user_id={USER_ID}`
*   **Backend Process** (`routers/telegram.py`):
    *   Fetches the bot's username (e.g., `@VibeletsBot`).
    *   Constructs a deep link: `https://t.me/<BOT_USERNAME>?start=<USER_ID>`.
    *   **Log**: "STAGE 1: Telegram Connect Link Generated".
*   **Response**: Returns the generated link.
*   **Frontend**: Redirects the user to this link.

### 2. User Interaction (Telegram Client)

*   **Action**: The link opens the Telegram app (or web version) directly to the bot's chat.
*   **Display**: The user sees a "Start" button at the bottom of the chat.
*   **Note**: The `user_id` parameter is hidden from the user in the UI but is passed internally when "Start" is clicked.

### 3. Webhook Delivery (Telegram -> Backend)

*   **Action**: User clicks "Start".
*   **Telegram Payload**: Sends a `POST` request to `/bot/telegram/webhook`.
    *   **Body** (Simplified):
        ```json
        {
          "update_id": 123456789,
          "message": {
            "message_id": 1,
            "from": {
              "id": 987654321,
              "is_bot": false,
              "first_name": "Kartikeya",
              "username": "kartik123"
            },
            "chat": {
              "id": 987654321,
              "type": "private"
            },
            "date": 1672531200,
            "text": "/start VL_TEST_USER"
          }
        }
        ```
    *   **Key Data**: The `text` field contains `/start {USER_ID}`.

### 4. Connection Processing (Backend Service)

*   **Service**: `services/telegram_service.py` -> `handle_update` -> `process_telegram_message`
*   **Logic**:
    1.  Detects the `/start` command.
    2.  Parses the argument (e.g., `VL_TEST_USER`).
    3.  **Log**: "STAGE 2: Received Callback/Start from Telegram".
    4.  **Database Update**: Calls `save_telegram_connection` to map:
        *   `vibelets_user_id`: "VL_TEST_USER"
        *   `telegram_chat_id`: "987654321" (Used for sending messages)
        *   `username`: "kartik123"
*   **Validation**: Ensures `user_id` is present; otherwise, treats it as a generic start (not a connection attempt).

### 5. Confirmation (Bot -> User)

*   **Action**: The backend sends a welcome message immediately after saving the connection.
*   **Method**: `helpers.telegram_api.send_telegram_message`
*   **Message**:
    > "👋 Hello! I'm the Vibelets Bot.
    > ✅ You are now successfully connected!
    > I can help you with insights about your ad campaigns."

## Database Storage (`db.json`)

The connection is stored in the `telegram` section of `db.json`:

```json
{
  "telegram": {
    "VL_TEST_USER": {
      "chat_id": "987654321",
      "username": "kartik123",
      "first_name": "Kartikeya",
      "last_name": null,
      "connected_at": "2026-01-29T13:47:52.123456",
      "connected": true
    }
  }
}
```

## Troubleshooting

*   **No Link Generated**: Check `TELEGRAM_BOT_TOKEN` in `.env`. The bot username fetches dynamically; if the token is invalid, this fails.
*   **No Webhook Event**: Ensure `ngrok` is running and the webhook URL is correctly set using `set_webhook_telegram.py`.
*   **"Account Not Connected" Message**: If the user clicks "Start" without a deep link (just `/start`), the system prompts them to go back to the dashboard to connect properly.
