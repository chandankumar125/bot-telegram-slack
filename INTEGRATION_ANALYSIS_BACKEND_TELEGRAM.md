# Backend Integration Analysis: Telegram

**Scope:** Analysis of Python-based backend implementation for Telegram integration.
**Components:** API Routers, Helper Modules, Services, Database Utilities.

---

## 1. Architecture Overview

The backend integration follows a 3-layer architecture (simplified compared to Slack):

1.  **Router Layer (`routers/telegram.py`)**: 
    *   Entry point for Webhook updates (`/webhook`).
    *   Manages user-facing connection endpoints (`/connect`, `/disconnect`, `/status`).
2.  **Service Layer (`services/telegram_service.py`)**: 
    *   Handles "Deep Linking" logic (`/start <token>`).
    *   Processes incoming messages and routes them to AI.
    *   Manages bot responses.
3.  **Database/Utils (`utils/db.py`)**: 
    *   Stores `chat_id` vs `user_id` mapping.
    *   Unlike Slack, no OAuth tokens are stored (only long-lived bot token in env).

---

## 2. Core Workflows

### A. Authentication (Deep Linking)
Telegram does not use OAuth 2.0 in the traditional sense. It uses **Deep Linking** to bind an external user ID to a Telegram Chat ID.

*   **Initiation:** `/bot/telegram/connect?user_id={uid}`
    *   Dynamically fetches the Bot Username (e.g., `@VibeletsBot`).
    *   Generates a link: `https://t.me/VibeletsBot?start={uid}`.
    *   **Logging:** JSON logs for "STAGE 1" Link Generation.
*   **Callback (via Webhook):** `/bot/telegram/webhook` -> `/start {uid}`
    *   User clicks "Start" in Telegram app.
    *   Backend receives a message update with text `/start {uid}`.
    *   **Logic:**
        *   Parses `{uid}` to identify the Vibelets User.
        *   Extracts `{chat_id}` and `username` from the update.
        *   **Logging:** JSON logs for "STAGE 2" Connection Callback.
    *   **Storage:** Saves `{uid}: {chat_id}` mapping to `db.json`.
    *   **Response:** Sends a "Welcome/Connected" message immediately.

### B. Event Handling (Webhooks)
*   **Endpoint:** `/bot/telegram/webhook`
*   **Security:** Relying on the secrecy of the Webhook URL (and `telegram-bot-api`'s implicit trust). *Note: Unlike Slack, we don't have a signature verification middleware here yet, relying on path obscurity or IP whitelisting is standard but `python-telegram-bot` handles the payload structure.*
*   **Structure:**
    *   Uses Pydantic model `TelegramUpdate` (or raw `dict`) to parse JSON.
    *   Offloads processing to `BackgroundTasks` (`handle_update`).

### C. Message & AI Logic
*   **Flow:**
    1.  User sends message: `How are my ads?`
    2.  `handle_update` detects it's a text message (not a command).
    3.  **Auth Check:** Looks up `chat_id` in `db.json` -> gets `user_id`.
    4.  **AI Resolution:** Calls `services.vibelets_service.resolve_query(user_id, text)`.
    5.  **Response:** Sends text back via `send_message(chat_id, response_text)`.

---

## 3. Key Components Analysis

| Component | Status | Key Features |
| :--- | :--- | :--- |
| `routers/telegram.py` | ✅ **Complete** | - Clean webhook endpoint<br>- Deep link generation<br>- Disconnect handler with user notification |
| `services/telegram_service.py` | ✅ **Complete** | - Uses `python-telegram-bot` wrapper<br>- Handles `/start` logic<br>- Routes AI queries |
| `helpers/telegram_api.py` | ✅ **Complete** | - Simplified wrapper for sending messages<br>- Webhook setup utility |

---

## 4. Current Test Coverage

*   **Webhook Setup:** `set_webhook_telegram.py` (Automates ngrok URL registration).
*   **Notification Test:** `test_notification_endpoint.py` (Verified push notifications to connected Telegram users).
*   **Backend Health:** `test_telegram_polling.py` (Optional legacy script for local polling tests).

## 5. Deployment Notes

*   **Long-Polling vs Webhooks:** The current architecture is designed for **Webhooks** (Production Ready).
*   **Token Lifecycle:** The Bot Token is long-lived. If compromised, it must be revoked via `@BotFather` and updated in `.env`. No automatic rotation required.
