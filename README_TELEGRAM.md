# ✈️ Telegram Integration Module - Master Documentation

This directory contains the complete implementation of the Vibelets Telegram Bot.
This `README` serves as the central index for all Telegram-related components, token architecture, and testing tools.

---

## 🔑 Token & Authentication Architecture

Unlike OAuth-based platforms (like Slack), Telegram uses a simpler token mechanism.

### **The "Long-Lived" Bot Token**
When you create a bot using **@BotFather**, Telegram gives you a single **long-lived bot token** (a string like `1234567890:ABCDEF...`).

*   **Purpose**: This token is used to authenticate your bot with the Telegram Bot API in every request you make via HTTPS.
*   **Properties**:
    *   **Bot token**: ✅ Yes (Long-lived)
    *   **Refresh token**: ❌ No (Not needed)
    *   **Token expiration**: ❌ No automatic expiry (Perpetual until revoked)
    *   **Manual revoke/regenerate**: ✅ Yes (Via @BotFather if connection is compromised)

---

## 📂 Code Structure & Architecture

The Telegram integration follows a modular 3-layer architecture:

### 1. **Helpers (The "Worker" Layer)**
*   **File:** `helpers/telegram_api.py`
*   **Purpose:** Wrappers for the `python-telegram-bot` or direct HTTP requests.
*   **Key Functions:**
    *   `send_telegram_message(chat_id, text)`: Sends asynchronous messages to users.
    *   `set_webhook(url)`: Configures where Telegram sends updates.

### 2. **Routers (The "API" Layer)**
*   **File:** `routers/telegram.py`
*   **Purpose:** HTTP Endpoints exposed to Telegram and the user's dashboard.
*   **Key Endpoints:**
    *   `POST /webhook`: Receives messages/commands from Telegram servers.
    *   `GET /connect`: Generates the "Deep Link" (`t.me/Bot?start=...`) for binding users.
    *   `POST /disconnect`: Unbinds a user from the database.
    *   `GET /status`: Checks if a Vibelets user is currently connected.

### 3. **Services (The "Logic" Layer)**
*   **File:** `services/telegram_service.py`
*   **Purpose:** Handles business logic and command processing.
*   **Key Logic:**
    *   `handle_update(payload)`: Processes incoming webhook data.
    *   `process_telegram_message`: Detects `/start` commands and handles connection logic.
    *   `get_bot_username()`: Caches the bot's username for link generation.

---

## 📚 Documentation Reference

| Document | Purpose |
| :--- | :--- |
| **[TELEGRAM_INTEGRATION_FLOW.md](./TELEGRAM_INTEGRATION_FLOW.md)** | Technical breakdown of the "Deep Linking" connection flow and data lifecycle. |

---

## 🛠️ Testing & Setup Tools

Use these scripts to manage and test the bot:

### 1. **Webhook Setup** (`set_webhook_telegram.py`)
*   **Purpose**: Tells Telegram API where to send events (your ngrok URL).
*   **Usage**: `python set_webhook_telegram.py` (Run this after starting ngrok).

### 2. **Notification Testing** (`test_notification_endpoint.py`)
*   **Purpose**: Tests the unified `/bot/notify` endpoint.
*   **Usage**: Modify the script to set `"platform": "telegram"` and run it to verify the bot can push messages to a connected user.

### 3. **Environment Setup**
Ensure your `.env` file has:
```ini
TELEGRAM_BOT_TOKEN="your_token_from_botfather"
# Note: No Client ID or Client Secret is needed for Telegram
```
