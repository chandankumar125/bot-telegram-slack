
# Slack Integration Flow: Frontend & Backend

This document maps the complete journey of connecting Slack to Vibelets, from the dashboard button click to the final database save.

---

## 1. Frontend: "Connect" Button Click
**File:** `static/js/app.js`

*   **User Action:** Clicks "Connect Slack" button.
*   **Logic:**
    *   Reads `user_id` from URL (or defaults to `VL_TEST_USER`).
    *   Redirects browser to Backend URL.
*   **Request Sent (Browser -> Backend):**
    ```http
    GET /bot/slack/install?user_id=VL_TEST_USER
    ```

---

## 2. Backend: Initiation (The "Handshake")
**File:** `routers/slack.py` -> `install_bot()`

*   **Receive:** `user_id` = "VL_TEST_USER"
*   **Action:**
    1.  Generates a unique `state` string: `VL_TEST_USER:<random_uuid>` (e.g., `VL_TEST_USER:28f9fc65`).
    2.  Builds the Slack Authorization URL.
*   **Response (Backend -> Browser):**
    *   `307 Temporary Redirect` -> `https://slack.com/oauth/v2/authorize?...`
    *   **Params sent to Slack:**
        *   `client_id`: your_app_client_id
        *   `scope`: `app_mentions:read,chat:write,...`
        *   `redirect_uri`: `https://...ngrok-url/bot/slack/oauth_callback`
        *   `state`: `VL_TEST_USER:28f9fc65`

---

## 3. User & Slack: Approval
*   **User Action:** User is taken to Slack.com, sees permissions screen, clicks "Allow".
*   **Slack Action:** Redirects user BACK to your specific `redirect_uri` with a temporary code.

---

## 4. Backend: Callback Processing
**File:** `routers/slack.py` -> `oauth_callback(code, state)`

*   **Receive:**
    *   `code`: `102944...` (Valid for 10 mins, single use)
    *   `state`: `VL_TEST_USER:28f9fc65`


*   **Action 1: Code Exchange (Server-to-Server)**
    *   Calls `helpers/slack_api.py` -> `authorize_slack_user(code)`
    *   **Sends (POST https://slack.com/api/oauth.v2.access):**
        ```json
        {
          "client_id": "...",
          "client_secret": "...",
          "code": "102944...",
          "redirect_uri": "..."
        }
        ```
    *   **Receives (JSON from Slack):**
        ```json
        {
          "ok": true,
          "access_token": "xoxe.xoxb-1-...",  // The Token we need!
          "refresh_token": "xoxe-1-...",      // If rotation enabled
          "expires_in": 43200,                // 12 hours
          "team": { "id": "T0A8...", "name": "Adsparkx" },
          "authed_user": { "id": "U0A8..." }  // The user who installed it
        }
        ```

*   **Action 2: User Identification**
    *   Parses `state` (`VL_TEST_USER:28f9fc65`) to recover `vibelets_user_id` -> `VL_TEST_USER`.

*   **Action 3: Fetch Extra Info (Server-to-Server)**
    *   Calls `helpers/slack_api.py` -> `get_slack_user_info(token, slack_user_id)`
    *   **Sends (GET https://slack.com/api/users.info):** `user=U0A8...`
    *   **Receives:** User profile data (including Email: `chandan...@...`).

*   **Action 4: Save to Database**
    *   Calls `utils/db.py` -> `save_slack_connection(...)`
    *   **Saves:**
        *   `teams/T0A8...`: Access Token, Refresh Token (System Level)
        *   `users/VL_TEST_USER/slack`: Connected=True, TeamID, Email (User Level)

*   **Action 5: Send Welcome Message**
    *   Calls `helpers/slack_api.py` -> `publish_slack_message(token, ...)`
    *   **Sends (POST https://slack.com/api/chat.postMessage):** "👋 Hello! You are connected!"

*   **Final Response (Backend -> Browser):**
    *   Redirects user back to Dashboard with success flag.
    *   `dashboard/?status=success&platform=slack...`

---

## 5. Summary of Files Involved

1.  **`static/js/app.js`**: Frontend trigger.
2.  **`routers/slack.py`**: The API controller. Orchestrates flow, handles redirects.
3.  **`helpers/slack_api.py`**: The "Worker". Talks to Slack API (requests/responses).
4.  **`utils/db.py`**: The Memory. Saves/Retrieves tokens.
5.  **`services/slack_service.py`**: The Logic. Uses tokens later for events/messages.

