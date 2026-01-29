# Backend Integration Analysis: WhatsApp

**Scope:** Analysis of Python-based backend implementation for WhatsApp Cloud API integration.
**Components:** API Routers, Helper Modules, Services, Database Utilities.

---

## 1. Architecture Overview

The backend integration follows the standard 4-layer architecture used in this project:

1.  **Router Layer (`routers/whatsapp.py`)**: 
    *   **Verify Endpoint (`GET /webhook`)**: Handshake for setting up the Meta connection (`hub.verify_token`).
    *   **Event Endpoint (`POST /webhook`)**: Receives all message events (`messages`).
    *   **Status Endpoint (`GET /status`)**: Lightweight check for Frontend Dashboard.
2.  **Service Layer (`services/whatsapp_service.py`)**: 
    *   **Message Processing**: Parses complex nested JSON from Meta.
    *   **Command Logic**: Handles "Connect <ID>" and "Disconnect" commands.
    *   **AI Routing**: Forwards conversational messages to `vibelets_service`.
3.  **Helper Layer (`helpers/whatsapp_api.py`)**: 
    *   **Signature Verification**: HMAC-SHA256 validation of `X-Hub-Signature-256`.
    *   **Graph API Wrapper**: Sends HTTP POST requests to `graph.facebook.com`.
4.  **Database Layer**: 
    *   Stores `whatsapp_id (phone)` <-> `user_id` mapping.

---

## 2. Core Workflows

### A. Authentication (User Binding)
Unlike Slack (OAuth) or Telegram (Deep Linking), WhatsApp API does NOT support passing custom parameters in a "Start" link.
*   **Method:** **"Click to Chat" + Manual Message**.
*   **Flow**:
    1.  Frontend Link: `https://wa.me/{BOT_NUMBER}?text=Connect {USER_ID}`
    2.  User clicks -> WhatsApp opens with pre-filled text.
    3.  User sends: "Connect VL_TEST_USER".
    4.  **Backend Logic (`handle_incoming_message`)**:
        *   Detects `Connect` keyword.
        *   Extracts `VL_TEST_USER`.
        *   Saves binding to `db.json`.
        *   Replies: "✅ Connected Successfully!"

### B. Event Handling (Webhooks)
*   **Security**: All incoming requests are verified against `WHATSAPP_APP_SECRET`.
    *   Failed signatures return `401 Unauthorized`.
*   **Structure**: 
    *   Meta sends a huge JSON payload wrapping the message inside `entry` -> `changes` -> `value` -> `messages`.
    *   We use `schemas/whatsapp.py` (Pydantic) to parse this safely.
*   **Async Processing**:
    *   The router immediately returns `200 OK` (required by Meta to stop retries).
    *   Actual processing happens in `BackgroundTasks`.

### C. Message & AI Logic
*   **Flow**:
    1.  User sends: "How are my ads?"
    2.  **Verification**: Is this phone number linked to a User ID in DB?
        *   If **No**: Reply with "Welcome! Please reply 'Connect <ID>'".
        *   If **Yes**: Forward text to `resolve_query(user_id, text)`.
    3.  **Response**: result is sent back via `helpers.send_whatsapp_message`.

---

## 3. Key Components Analysis

| Component | Status | Key Features |
| :--- | :--- | :--- |
| `routers/whatsapp.py` | ✅ **Complete** | - Implements Meta's challenge/response handshake.<br>- Validates Signatures using headers. |
| `services/whatsapp_service.py` | ✅ **Complete** | - Handles complex JSON drill-down.<br>- Implements specific "Connect" command logic.<br>- Supports Contact Name extraction. |
| `helpers/whatsapp_api.py` | ✅ **Complete** | - Security calculation for SHA256.<br>- Clean requests wrapper for Graph API v17.0. |

---

## 4. Configuration & Constraints

*   **24-Hour Window**: The bot can only reply to users who have messaged it within the last 24 hours. (Currently handled by waiting for user initiation).
*   **Phone Number ID**: Hardcoded in `.env`. This represents the *sender identity* in Graph API.
*   **Bot Number**: Defined in `.env` (`WHATSAPP_BOT_NUMBER`) for generating the frontend link.

## 5. Current Test Coverage
*   **Local Webhook Test:** `test_whatsapp_local.py` (Simulates a webhook hit with valid signature generation).
*   **Notification Test:** `send_test_notification.py` (Can target WhatsApp users via the unified notification service).
