# 🚀 Slack Integration Module - Master Documentation

 This directory contains the complete implementation of the Vibelets Slack Bot.
 This `README` serves as the central index for all Slack-related components, documentation, and testing tools.

---

## 📂 Code Structure & Architecture

The Slack integration follows a modular 4-layer architecture:

### 1. **Helpers (The "Worker" Layer)**
*   **File:** `helpers/slack_api.py`
*   **Purpose:** Pure, stateless functions to interact with Slack API.
*   **Key Functions:**
    *   `authorize_slack_user(code)`: Exchanges OAuth code for tokens.
    *   `refresh_slack_token(token)`: Handles token rotation logic.
    *   `verify_slack_request(...)`: Validates `X-Slack-Signature`.
    *   `publish_slack_message(...)`: Sends DMs and Channel messages.

### 2. **Routers (The "API" Layer)**
*   **File:** `routers/slack.py` (Core)
*   **Purpose:** HTTP Endpoints exposed to the outside world for Slack.
*   **Key Endpoints:** `GET  /install`, `GET /oauth_callback`, `POST /events`, `GET /status`.
*   **File:** `routers/notifications.py` (Trigger)
*   **Purpose:** Unified endpoint to push proactive messages to bots.
*   **Key Endpoint:** `POST /bot/notify` - Sends messages using the helper layer.

### 3. **Services (The "Logic" Layer)**
*   **Files:**
    *   `services/slack_service.py`: Business logic for Slack (Token storage, Event routing).
    *   `services/vibelets_service.py`: AI Agent logic that processes user queries.
*   **Purpose:** Connects the API (Router) to the Database and AI, using Helpers for output.

### 4. **Schemas (The "Data" Layer)**
*   **Files:**
    *   `schemas/vibelets.py` (V): AI Agent & Notification models.
    *   `schemas/bot.py` (B): Generic Bot structures.
    *   `schemas/slack.py` (S): Slack-specific Event models.
*   **Purpose:** Pydantic models used to validate incoming requests and internal data structures.

---

## 📚 Documentation Reference

We have detailed documentation for every aspect of this integration:

| Document | Purpose | Audience |
| :--- | :--- | :--- |
| **[SLACK_INTEGRATION_FLOW.md](./SLACK_INTEGRATION_FLOW.md)** | Technical deep-dive into the OAuth & Event sequences. | Backend Devs |
| **[SLACK_WORKFLOW_HANDOFF.md](./SLACK_WORKFLOW_HANDOFF.md)** | API Contract & Agreement between Frontend/Backend. | Full Stack Team |
| **[INTEGRATION_ANALYSIS_BACKEND.md](./INTEGRATION_ANALYSIS_BACKEND.md)** | Analysis of the Python architecture & workflows. | Architects |
| **[INTEGRATION_ANALYSIS_FRONTEND.md](./INTEGRATION_ANALYSIS_FRONTEND.md)** | Analysis of the Dashboard UI & Javascript flow. | Frontend Devs |

---

## 🛠️ Testing Tools

Use these scripts to verify functionality during development:

### 1. **Webhook Verification** (`test_webhook_slack.py`)
*   **Purpose:** Simulates an incoming POST request from Slack to your local machine.
*   **Authenticity:** Generates valid valid `X-Slack-Signature` using your `.env` secret.
*   **Use Case:** Verify `routers/slack.py` handles events correctly without needing a real Slack workspace.

### 2. **Integration Test Suite** (`test_slack_integration.py`)
*   **Purpose:** End-to-end verification of the backend.
*   **Checks:**
    *   ✅ Backend Health (Ping)
    *   ✅ Auth Redirect URLs
    *   ✅ Database Connection Status
    *   ✅ Token Rotation Mode (Mode 1 vs Mode 2)
    *   ✅ Notification Delivery (Real message to Slack)


---
