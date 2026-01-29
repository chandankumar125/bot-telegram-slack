# Frontend Integration Analysis: Telegram

**Scope:** Analysis of Javascript-based frontend implementation for Telegram integration.
**File:** `static/js/app.js` and `static/index.html`.

---

## 1. User Experience Flow

The Telegram flow differs from Slack because it requires the user to leave the browser, interact with an external app (Telegram), and then return.

### A. Initialization & Link Generation
*   **Trigger:** `DOMContentLoaded` event calls `fetchTelegramLink(userId)`.
*   **API Call:** `GET /bot/telegram/connect?user_id={uid}`.
*   **Response:** JSON `{ "link": "https://t.me/VibeletsBot?start={uid}" }`.
*   **Action:** Javascript dynamically updates the `href` of the "Connect Telegram" button in the DOM.

### B. Connection Workflow (The "Deep Link" Pattern)
*   **Action:** User clicks "Connect Telegram".
*   **Behavior:**
    *   Opens the Telegram App (or Web) in a **new tab** (`target="_blank"`).
    *   User clicks "Start" inside Telegram.
    *   **Crucial UX Challenge:** The connection happens in the *background* (Telegram -> Backend Webhook). The frontend page is unaware of this action initially.

### C. The "Auto-Refresh" Logic (UX Enhancement)
*   **Problem:** Unlike Slack (which redirects *back* to our page), Telegram keeps the user in their app. When the user alt-tabs back to our Dashboard, the status would ostensibly still show "Not Connected".
*   **Solution:** We implemented a `window.addEventListener('focus', checkAllStatuses)` listener.
*   **Flow:**
    1.  User returns to the Dashboard tab.
    2.  Browser fires `focus` event.
    3.  `checkTelegramStatus` is triggered immediately.
    4.  Backend returns `connected: true`.
    5.  UI updates to Green "Connected" state instantly without a manual page reload.

### D. Disconnection Workflow
*   **Action:** User clicks "Disconnect" (Red button).
*   **Safety:** Browser `confirm()` dialog.
*   **API Call:** `POST /bot/telegram/disconnect`.
*   **Feedback:** Toast notification "Disconnected successfully" and UI revert to grey "Not Connected".

---

## 2. API Utilization

| Frontend Function | Backend Endpoint | Method | Purpose |
| :--- | :--- | :--- | :--- |
| `fetchTelegramLink` | `/bot/telegram/connect` | `GET` | Fetches the unique deep-link with the user's ID embedded. |
| `checkTelegramStatus` | `/bot/telegram/status` | `GET` | Checks if the user has successfully clicked "Start". |
| `disconnectPlatform` | `/bot/telegram/disconnect` | `POST` | Unbinds the user in the database. |

---

## 3. UI Component Analysis (`index.html`)

*   **Card Design:** Matches the Slack card for consistency but uses Telegram branding colors (`#24A1DE`).
*   **Status Indicators:**
    *   **Green Dot + Border:** Visually confirms the active connection.
    *   **Username Display:** Shows `@username` (e.g., `@kartik123`) retrieved from the status endpoint, giving personal confirmation.

## 4. Key Code Highlights (`app.js`)

```javascript
// 1. Fetching the Link (Async)
async function fetchTelegramLink(userId) {
    const res = await fetch(`/bot/telegram/connect?user_id=${userId}`);
    const data = await res.json();
    // Updates the button href with 'https://t.me/...'
}

// 2. The Focus Listener (UX Polish)
window.addEventListener('focus', checkAllStatuses);
```

This implementation ensures a seamless experience even though the actual "Connection" event happens off-platform.
