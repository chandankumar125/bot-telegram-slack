# Frontend Integration Analysis: WhatsApp

**Scope:** Analysis of Javascript-based frontend implementation for WhatsApp integration.
**File:** `static/js/app.js` and `static/index.html`.

---

## 1. User Experience Flow

The WhatsApp flow is similar to Telegram (leaving the browser) but relies on a "Click to Chat" API that pre-fills a message instead of a deep-link parameter.

### A. Initialization & Link Generation
*   **Trigger:** `DOMContentLoaded` event calls `fetchWhatsAppLink(userId)`.
*   **API Call:** `GET /bot/whatsapp/connect?user_id={uid}`.
*   **Response:** JSON `{ "link": "https://wa.me/1555..?text=Connect%20{uid}" }`.
*   **Action:** Javascript dynamically updates the `href` of the "Connect WhatsApp" button.

### B. Connection Workflow (Click-to-Chat)
*   **Action:** User clicks "Connect WhatsApp".
*   **Behavior:**
    *   Opens `api.whatsapp.com` (or the specific `wa.me` link) in a **new tab** (`target="_blank"`).
    *   **User Action Required**: The user **must press Send** in their WhatsApp app to trigger the webhook.
    *   **Crucial Difference**: Unlike Telegram (where clicking "Start" is a system action), on WhatsApp, the user sends a literal text message.

### C. The "Auto-Refresh" Logic
*   **Problem:** The connection event (User sending message) happens on the phone/desktop app, not the browser.
*   **Solution:** Same as Telegram, we rely on the `focus` event listener.
*   **Flow:**
    1.  User sends message in WhatsApp app.
    2.  User switches back to Dashboard tab.
    3.  Browser fires `focus` event -> calls `checkWhatsAppStatus`.
    4.  Backend confirms binding exists in DB.
    5.  UI updates to Green "Connected" state instantly.

### D. Disconnection Workflow
*   **Action:** User clicks "Disconnect" (Red button).
*   **Safety:** Browser `confirm()` dialog.
*   **API Call:** `POST /bot/whatsapp/disconnect`.
*   **Feedback:** Toast notification and UI revert.

---

## 2. API Utilization

| Frontend Function | Backend Endpoint | Method | Purpose |
| :--- | :--- | :--- | :--- |
| `fetchWhatsAppLink` | `/bot/whatsapp/connect` | `GET` | Fetches the `wa.me` link pre-filled with the user's ID. |
| `checkWhatsAppStatus` | `/bot/whatsapp/status` | `GET` | Checks if the user's phone number is linked in `db.json`. |
| `disconnectPlatform` | `/bot/whatsapp/disconnect` | `POST` | Unbinds the user in the database. |

---

## 3. UI Component Analysis (`index.html`)

*   **Card Design:** Uses WhatsApp Brand Green (`#25D366`).
*   **Status Indicators:**
    *   **Connected State:** Displays the user's **WhatsApp Name** (retrieved from the status endpoint) to provide confidence that the correct account was linked.
    *   **Fallback:** If name is unavailable, shows "Linked".

## 4. Key Code Highlights (`app.js`)

```javascript
// 1. Fetching the Link (Async)
async function fetchWhatsAppLink(userId) {
    const res = await fetch(`/bot/whatsapp/connect?user_id=${userId}`);
    // ... updates DOM
}

// 2. Shared Focus Listener handles WhatsApp too
window.addEventListener('focus', checkAllStatuses);
```

### UX Consideration
Since WhatsApp requires the user to manually hit "Send", there is a slightly higher friction than Telegram's "Start" button. The Dashboard UI relies on the user completing this action for the Status Check to pass.
