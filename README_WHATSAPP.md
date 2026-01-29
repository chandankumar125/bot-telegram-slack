# 📱 WhatsApp Integration Module - Master Documentation

This directory contains the implementation of the Vibelets WhatsApp Bot using the **WhatsApp Cloud API** (Meta).

---

## 🔐 1. Authorization & Token Architecture

Unlike Slack (which uses OAuth 2.0 to impersonate users) or Telegram (which uses a simple Bot Token), WhatsApp Business API is stricter.

### **How we "Authorize" (The System User)**
*   **Concept**: The bot does not "login" as a user. Instead, it acts as a **System User** belonging to your Meta Business Manager.
*   **The Token**: We use a `WHATSAPP_ACCESS_TOKEN` (Bearer Token) in `.env`.
    *   **Current Setup**: This token authorizes *our server* to send messages **on behalf of the Business Number**.
    *   **User "Auth"**: The *End User* does not authorize via OAuth. Instead, they **bind** their account by messaging `Connect <ID>`.

### **Token Refresh Strategy** 🔄
*   **Status**: ❌ **No Auto-Refresh Logic Implemented.**
*   **Why?**
    *   Development tokens expire in **24 hours**.
    *   **Production System User Tokens** can be generated to be **Permanent** (Never expire).
    *   **Recommendation**: Generate a Permanent Access Token in Meta Business Settings -> System Users, so no code-based refreshing is ever needed.

---

## 🛡️ 2. Webhook Verification (Security)

When Meta sends a message to our URL (`/bot/whatsapp/webhook`), we perform two checks:

### **A. Verification Handshake (The "Hello")**
*   **When**: Only once, when you setup the URL in the Meta Dashboard.
*   **Logic**:
    *   Meta sends: `hub.verify_token` + `hub.challenge`.
    *   We check: Does `hub.verify_token` match our `.env` value?
    *   We respond: With `hub.challenge`.
*   **Result**: Meta confirms "Okay, this server belongs to you."

### **B. Request Integrity (The "Signature")**
*   **When**: Every single message payload.
*   **Logic**:
    *   Meta hashes the payload using your **App Secret**.
    *   Meta sends this hash in the header `X-Hub-Signature-256`.
    *   **Our Code (`helpers.whatsapp_api.verify_whatsapp_signature`)**: Re-calculates the hash using our local `WHATSAPP_APP_SECRET`.
    *   **Comparison**: If hashes don't match, we reject the request (401). This prevents hackers from faking messages.

---

## 📤 3. Publishing Messages

### **The "24-Hour Window" Rule**
*   **Observation**: You might see errors like "Failed to send".
*   **Reason**: WhatsApp forbids bots from messaging users *unless* the user has messaged the bot in the last **24 hours**.
*   **Solution**:
    1.  **Session Messages**: If within 24h window -> Free-form text allowed.
    2.  **Template Messages**: If outside 24h window -> MUST use a pre-approved Template (e.g., `hello_world`).

### **Implementation**
*   **File**: `helpers/whatsapp_api.py` -> `send_whatsapp_message`.
*   **Protocol**: HTTP POST to `https://graph.facebook.com/v17.0/{PHONE_ID}/messages`.

---

## 🗃️ Folder Structure

| Layer | File | Purpose |
| :--- | :--- | :--- |
| **Router** | `routers/whatsapp.py` | Webhook receiver (`/webhook`) & Verification logic. |
| **Service** | `services/whatsapp_service.py` | Command processor (`Connect`, `Disconnect`) & AI handoff. |
| **Helper** | `helpers/whatsapp_api.py` | Raw HTTP wrapper for Graph API & Signature Validation. |
