
# Backend Integration Analysis: Slack

**Scope:** Analysis of Python-based backend implementation for Slack integration.
**Components:** API Routers, Helper Modules, Services, Database Utilities.

---

## 1. Architecture Overview

The backend integration follows a 4-layer architecture:
1.  **Router Layer (`routers/slack.py`)**: Entry point for HTTP requests (Install, Callback, Events).
2.  **Service Layer (`services/slack_service.py`)**: Business logic (Token rotation, Event processing, DM handling).
3.  **Helper Layer (`helpers/slack_api.py`)**: Stateless wrappers for Slack API calls (Authorization, Messaging).
4.  **Database/Utils (`utils/db.py`)**: Persistence layer for tokens and user mapping.

---

## 2. Core Workflows

### A. Authentication (OAuth 2.0)
*   **Initiation:** `/bot/slack/install`
    *   Generates a state string combining `user_id` and a random UUID.
    *   Redirects to Slack's Authorize URL with requested scopes (`app_mentions:read`, `chat:write`, etc.).
    *   **Logging:** Detailed JSON logs for "STAGE 1" redirect.
*   **Callback:** `/bot/slack/oauth_callback`
    *   Exchanges temporary `code` for `access_token` and `refresh_token` using `helpers/slack_api.py`.
    *   **Logging:** Detailed JSON logs for "STAGE 2" callback and Token verification.
    *   **User Mapping:** Retrieves user email via `users.info` to enrich profile data.
    *   **Storage:** Saves tokens to `db.json` (Teams table for tokens, Users table for mapping).
    *   **Post-Auth:** Sends a "Welcome" DM to the user immediately upon connection.

### B. Event Handling (Webhooks)
*   **Endpoint:** `/bot/slack/events`
*   **Security:** Verifies `X-Slack-Signature` using `helpers.verify_slack_request` to prevent replay attacks and spoofing.
*   **Processing:**
    *   Handles `url_verification` (Slack handshake).
    *   Queues other events (messages, mentions) to `BackgroundTasks` to prevent timeout.
*   **Logic:**
    *   Identifies the user via `slack_user_id`.
    *   Checks if user is connected in `db.json`.
    *   If connected: Routes query to AI agent (`vibelets_service`).
    *   If disconnected: Sends a polite "Please Connect" prompt.

### C. Token Rotation (Security)
*   **Mechanism:** Implemented in `services/slack_service.py` -> `ensure_valid_token`.
*   **Trigger:** Checks token expiry before every API call.
*   **Action:** If expired (< 5 mins left), calls `helpers.refresh_slack_token` to swap the refresh token for a new pair.
*   **Persistence:** Updates `db.json` with the new keys immediately.

### D. Interactive Query Logic (AI Insights)
*   **Trigger:** User sends a DM or mentions the bot (`@Vibelets How are my ads?`).
*   **Flow:**
    1.  `routers/slack.py`: Receives event, verifies signature, offloads to `services/slack_service.py`.
    2.  `services/slack_service.py`: 
        *   Ignores bot's own messages.
        *   Checks if the user is linked in `db.json`.
        *   **Call:** Passes the message text to `services/vibelets_service.resolve_query`.
    3.  `services/vibelets_service.py`:
        *   Checks API Key / Mode (Dummy vs Real).
        *   **AI:** Calls Gemini (or Vibelets Core API) with the user query.
        *   **Return:** Gets the implementation/insight text.
    4.  `services/slack_service.py`:
        *   **Response:** Calls `helpers.publish_slack_message` with the AI's answer.
        *   **Result:** User sees the answer in Slack thread/DM.

---

## 3. Key Components Analysis

| Component | Status | Key Features |
| :--- | :--- | :--- |
| `helpers/slack_api.py` | ✅ **Complete** | Standardized requests. Detailed Debug Logging. Handles API Errors. |
| `routers/slack.py` | ✅ **Complete** | Clean routing. Good error handling (HTTP 400/500). Separation of concerns. |
| `services/slack_service.py` | ✅ **Complete** | **Refactored:** Now uses `helpers` exclusively (no direct `WebClient`). Smart token retrieval. |
| `db.json` Structure | ✅ **Complete** | Separates **User Identity** (Email/Link) from **Team Identity** (Tokens). |

---

## 4. Current Test Coverage
*   **Notification Test:** `test_notification_endpoint.py` verifies the `/notify` pipeline.
*   **Internal Integration Test:** `test_slack_integration.py` verifies Health, Auth Redirects, DB Status, and Token Rotation Mode.

## 5. Potential Enhancements (Future)
*   **Slash Commands:** Support for `/vibelets` command is currently missing (requires new endpoint).
*   **Interactive Components:** Button click handling (`block_actions`) is not implemented.
*   **Async DB:** `utils/db.py` uses blocking File I/O. For high scale, migrate to Async SQL/Redis.
