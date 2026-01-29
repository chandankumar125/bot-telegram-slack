# Complete Flow: Backend → Slack → User Query → Backend Response

This guide shows the complete flow from sending notifications to receiving and responding to user queries.

## 📋 Complete Flow Diagram

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Backend   │────────▶│  Slack Bot   │────────▶│    User     │
│  (FastAPI)  │         │   (Channel)  │         │  (Slack)    │
└─────────────┘         └──────────────┘         └─────────────┘
      │                        │                        │
      │                        │                        │
      │  1. Send Notification  │                        │
      │────────────────────────▶│                       │
      │                        │                        │
      │                        │  2. User sees message  │
      │                        │───────────────────────▶│
      │                        │                        │
      │                        │  3. User asks question │
      │                        │◀───────────────────────│
      │                        │                        │
      │  4. Slack sends webhook │                        │
      │◀────────────────────────│                        │
      │                        │                        │
      │  5. Process query       │                        │
      │  6. Get AI response     │                        │
      │                        │                        │
      │  7. Send response      │                        │
      │────────────────────────▶│                        │
      │                        │  8. User sees response │
      │                        │───────────────────────▶│
      │                        │                        │
```

## 🔄 Step-by-Step Flow

### Step 1: Backend Sends Notification to Slack

**What happens:**
- Your backend receives a notification request
- Backend calls Slack API to post message in channel
- Message appears in Slack channel

**Code Example:**
```python
# From your backend or external service
import requests

response = requests.post(
    "http://localhost:8000/bot/notify",
    json={
        "alert_id": "alert-123",
        "platform": "slack",
        "channel_id": "C1234567890",  # Your channel ID
        "title": "🚨 Server Alert",
        "summary": "CPU usage is at 95%. Check server logs."
    }
)
```

**What user sees in Slack:**
```
#bot-testing channel
─────────────────────────────
Vibelets Bot  [10:30 AM]
🚨 Server Alert
CPU usage is at 95%. Check server logs.
─────────────────────────────
```

### Step 2: User Sees Notification

**What happens:**
- User opens Slack channel
- Sees the notification message from bot
- Reads the alert/notification

### Step 3: User Sends Query

**What happens:**
- User types a question in the Slack channel
- Example: "What caused this alert?"
- User presses Enter

**What user types:**
```
#bot-testing channel
─────────────────────────────
You  [10:31 AM]
What caused this alert?
─────────────────────────────
```

### Step 4: Slack Sends Webhook to Backend

**What happens:**
- Slack detects message in channel
- Slack sends HTTP POST to your webhook URL
- Your backend receives the event

**Webhook URL:**
```
POST https://your-ngrok-url.ngrok.io/bot/slack/events
```

**Payload Slack sends:**
```json
{
  "type": "event_callback",
  "event": {
    "type": "message",
    "text": "What caused this alert?",
    "channel": "C1234567890",
    "user": "U1234567890",
    "ts": "1234567890.123456"
  }
}
```

### Step 5: Backend Processes Query

**What happens:**
- Backend receives webhook at `/bot/slack/events`
- Extracts the user's question
- Calls Vibelets AI API (if configured)
- Gets AI response

**Backend Code Flow:**
```python
# routers/slack.py receives webhook
# services/slack_service.py handles event
# services/vibelets_service.py calls AI
```

### Step 6: Backend Gets AI Response

**What happens:**
- Backend sends query to Vibelets AI
- AI processes the question
- AI returns answer

**Code:**
```python
# In services/vibelets_service.py
def resolve_query(user_id, question):
    response = requests.post(
        f"{VIBELETS_BASE_URL}/bot/resolve",
        headers={"Authorization": f"Bearer {VIBELETS_API_KEY}"},
        json={"user_id": user_id, "question": question}
    )
    return response.json().get("answer", "No response found")
```

### Step 7: Backend Sends Response to Slack

**What happens:**
- Backend uses Slack API to post message
- Message is sent to the same channel
- User receives the response

**Code:**
```python
# In services/slack_service.py
def send_message(channel_id: str, text: str):
    client.chat_postMessage(channel=channel_id, text=text)
```

### Step 8: User Sees Response

**What happens:**
- User sees bot's response in Slack channel
- Response appears below their question

**What user sees:**
```
#bot-testing channel
─────────────────────────────
Vibelets Bot  [10:31 AM]
🚨 Server Alert
CPU usage is at 95%. Check server logs.
─────────────────────────────
You  [10:31 AM]
What caused this alert?
─────────────────────────────
Vibelets Bot  [10:31 AM]
Based on the server logs, the high CPU usage 
was caused by a memory leak in the application 
process. The process was consuming excessive 
resources due to unclosed database connections.
─────────────────────────────
```

## 🛠️ How to Test the Complete Flow

### Prerequisites

1. **Server running:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. **ngrok running:**
   ```bash
   .\ngrok.exe http 8000
   ```

3. **Bot configured:**
   - Bot token in `.env` file
   - Webhook URL verified in Slack
   - Bot invited to channel

### Test Step 1: Send Notification

**Option A: Using Python script**
```bash
python send_test_notification.py C1234567890 "Server Alert" "CPU usage is high"
```

**Option B: Using curl**
```bash
curl -X POST http://localhost:8000/bot/notify ^
  -H "Content-Type: application/json" ^
  -d "{\"alert_id\": \"test-123\", \"platform\": \"slack\", \"channel_id\": \"C1234567890\", \"title\": \"Test Alert\", \"summary\": \"This is a test\"}"
```

**Option C: Using Python requests**
```python
import requests

response = requests.post(
    "http://localhost:8000/bot/notify",
    json={
        "alert_id": "test-123",
        "platform": "slack",
        "channel_id": "YOUR_CHANNEL_ID",
        "title": "🚨 Server Alert",
        "summary": "CPU usage is at 95%. Check server logs."
    }
)
print(response.json())
```

### Test Step 2: Check Slack

1. Open Slack
2. Go to your channel (e.g., `#bot-testing`)
3. You should see the notification message

### Test Step 3: Send Query from Slack

1. In the same Slack channel
2. Type a question: "What caused this alert?"
3. Press Enter

### Test Step 4: Verify Backend Received Query

**Check server logs:**
```
INFO: 127.0.0.1:xxxxx - "POST /bot/slack/events HTTP/1.1" 200 OK
```

**Check ngrok web interface:**
- Open: http://127.0.0.1:4040
- You'll see the incoming request from Slack
- Click to inspect payload and response

### Test Step 5: Verify Response in Slack

1. Check Slack channel
2. Bot should respond with answer
3. Response appears below your question

## 📝 Complete Example Code

### Backend Endpoint: Send Notification

```python
# POST /bot/notify
# routers/notifications.py

@router.post("/notify")
def notify(payload: BotNotification):
    return push_notification(payload)
```

### Backend Endpoint: Receive Query

```python
# POST /bot/slack/events
# routers/slack.py

@router.post("/events")
async def slack_events(request: Request, ...):
    # Receives webhook from Slack
    # Processes user query
    # Returns response
```

## 🔍 Monitoring the Flow

### 1. Server Logs

Watch your uvicorn terminal:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:xxxxx - "POST /bot/notify HTTP/1.1" 200 OK
INFO:     127.0.0.1:xxxxx - "POST /bot/slack/events HTTP/1.1" 200 OK
```

### 2. ngrok Web Interface

Open: http://127.0.0.1:4040
- See all incoming requests
- Inspect payloads
- Check responses

### 3. Slack Channel

- See notification messages
- See user queries
- See bot responses

## 🎯 Quick Test Script

```python
# test_complete_flow.py
import requests
import time

BASE_URL = "http://localhost:8000"
CHANNEL_ID = "YOUR_CHANNEL_ID"  # Replace with your channel ID

print("Step 1: Sending notification...")
response = requests.post(
    f"{BASE_URL}/bot/notify",
    json={
        "alert_id": f"test-{int(time.time())}",
        "platform": "slack",
        "channel_id": CHANNEL_ID,
        "title": "🚨 Test Alert",
        "summary": "This is a test. Ask: 'What caused this alert?'"
    }
)
print(f"Notification sent: {response.json()}")

print("\nStep 2: Go to Slack and ask a question in the channel")
print("Step 3: Watch server logs and ngrok interface")
print("Step 4: Check Slack for bot response")
```

## ✅ Checklist

Before testing, ensure:

- [ ] Server is running: `uvicorn main:app --reload --port 8000`
- [ ] ngrok is running: `.\ngrok.exe http 8000`
- [ ] Webhook URL is verified in Slack settings
- [ ] Bot is invited to channel: `/invite @YourBotName`
- [ ] `.env` file has `SLACK_BOT_TOKEN` set
- [ ] Channel ID is correct (starts with `C`)

## 🐛 Troubleshooting

### Notification not appearing?
- Check bot is invited to channel
- Verify channel ID is correct
- Check `SLACK_BOT_TOKEN` is set
- Check server logs for errors

### Bot not responding to queries?
- Check webhook URL is verified
- Verify ngrok is running
- Check server logs for incoming requests
- Verify `SLACK_SIGNING_SECRET` is set

### Bot responds with error?
- Check `VIBELETS_API_KEY` is set (if using AI)
- Verify API key is valid
- Check server logs for API errors
