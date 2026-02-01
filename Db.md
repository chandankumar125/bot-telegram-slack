1️⃣ slack_workspaces table
CREATE TABLE public.slack_workspaces (
    id BIGSERIAL PRIMARY KEY,
    team_id TEXT UNIQUE NOT NULL,
    team_name TEXT,
    bot_user_id TEXT,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE,
    installed_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

2️⃣ slack_user_connections table

(Links adu_users ↔ Slack workspace users)

CREATE TABLE public.slack_user_connections (
    id BIGSERIAL PRIMARY KEY,
    workspace_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,

    slack_user_id TEXT UNIQUE NOT NULL,
    slack_email TEXT,
    slack_username TEXT,

    is_connected BOOLEAN DEFAULT TRUE,
    connected_at TIMESTAMPTZ DEFAULT NOW(),
    disconnected_at TIMESTAMPTZ,

    CONSTRAINT fk_workspace
        FOREIGN KEY (workspace_id)
        REFERENCES public.slack_workspaces(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_user
        FOREIGN KEY (user_id)
        REFERENCES public.adu_users(id)
        ON DELETE CASCADE
);
### Access
2️⃣ Access using SQL (most common & powerful)
View all Slack workspaces
SELECT * FROM public.slack_workspaces;

View all Slack users connected
SELECT * FROM public.slack_user_connections;

View events
SELECT * FROM public.slack_event_logs
ORDER BY processed_at DESC;

3️⃣ (Optional) slack_event_logs table

(for audit / debugging)

CREATE TABLE public.slack_event_logs (
    id BIGSERIAL PRIMARY KEY,
    event_id TEXT UNIQUE NOT NULL,
    team_id TEXT NOT NULL,
    event_type TEXT,
    event_payload JSONB,
    processed_at TIMESTAMPTZ DEFAULT NOW()
);

4️⃣ Helpful indexes (recommended)
CREATE INDEX idx_slack_user_connections_user_id
ON public.slack_user_connections(user_id);

CREATE INDEX idx_slack_user_connections_workspace_id
ON public.slack_user_connections(workspace_id);

CREATE INDEX idx_slack_event_logs_team_id
ON public.slack_event_logs(team_id);

2️⃣ Access using SQL (most common & powerful)
View all Slack workspaces
SELECT * FROM public.slack_workspaces;

View all Slack users connected
SELECT * FROM public.slack_user_connections;

View events
SELECT * FROM public.slack_event_logs
ORDER BY processed_at DESC;

3️⃣ Access with JOINs (real use case)
Get Slack info for an app user
SELECT
    u.id AS user_id,
    u.email,
    sw.team_name,
    suc.slack_username,
    suc.slack_email
FROM adu_users u
JOIN slack_user_connections suc ON suc.user_id = u.id
JOIN slack_workspaces sw ON sw.id = suc.workspace_id
WHERE u.id = 1;

Find all users in a Slack workspace
SELECT
    sw.team_name,
    suc.slack_user_id,
    suc.slack_username
FROM slack_user_connections suc
JOIN slack_workspaces sw ON sw.id = suc.workspace_id
WHERE sw.team_id = 'T12345678';

4️⃣ Access from Python backend (psycopg2 example)
cursor.execute("""
    SELECT sw.team_name, suc.slack_user_id
    FROM slack_user_connections suc
    JOIN slack_workspaces sw ON sw.id = suc.workspace_id
    WHERE suc.user_id = %s
""", (user_id,))

rows = cursor.fetchall()

5️⃣ Common real-world queries you’ll need
🔹 Check if workspace already installed
SELECT id FROM slack_workspaces WHERE team_id = 'T123';

🔹 Check if user connected Slack
SELECT is_connected
FROM slack_user_connections
WHERE user_id = 5;

🔹 Store Slack event
INSERT INTO slack_event_logs (event_id, team_id, event_type, event_payload)
VALUES ('Ev123', 'T123', 'message', '{"text":"hello"}');

### 
1️⃣ Dummy data for slack_workspaces
INSERT INTO public.slack_workspaces
(team_id, team_name, bot_user_id, access_token, refresh_token, token_expires_at)
VALUES
('T1001', 'Adsparkx Marketing', 'B1001', 'xoxb-token-1', 'xoxr-token-1', NOW() + INTERVAL '90 days'),
('T1002', 'Sales Automation', 'B1002', 'xoxb-token-2', 'xoxr-token-2', NOW() + INTERVAL '90 days'),
('T1003', 'Product Team', 'B1003', 'xoxb-token-3', 'xoxr-token-3', NOW() + INTERVAL '90 days');

2️⃣ Dummy data for slack_user_connections
3️⃣ Dummy data for slack_event_logs

# routes(url)-- controler(logic)-- frontend()-- database(postgress)

### The Slack integration flow has been successfully updated to use PostgreSQL.

Here is a summary of the changes:

# Database Integration (utils/postgres_db.py):
1. Created a new module to handle all PostgreSQL interactions.
2. Implemented functions to save connections (slack_workspaces, slack_user_connections), retrieve tokens, and handle disconnects.
3. Matches the schema provided in Db.md.

# Configuration:
1. Updated .env with PostgreSQL credentials (defaulted to localhost, postgres, root). Please check and update these credentials in your .env file.
2. Updated config.py to load these database settings.
3. Added psycopg2-binary to requirements.txt and installed it.
# Router (routers/slack.py):
1. Refactored oauth_callback to save connection data to PostgreSQL.
2. Refactored disconnect_bot and get_connection_status to query PostgreSQL.
3. Added validation for user_id to ensure it's a valid integer matching adu_users.

# Service Logic (services/slack_service.py):
1. Updated handle_event to fetch tokens and user mappings from PostgreSQL.
2. Refactored send_message_to_user to efficiently query the database (joins) rather than scanning a JSON file.
3. Ensured resolve_query receives the correct internal Vibelets User ID instead of the Slack ID.

# Notifications (services/vibelets_service.py):
1. Updated to fetch Slack connections from PostgreSQL when sending push notifications.


### Correct Flow for Notification:

1. Frontend/Postman sends user_id="1".
2. push_notification calls get_slack_connection("1").
3. get_slack_connection returns slack_user_id(e.g., U12345).
4. slack_send_message calls get_connection_by_slack_user_id("U12345") to find the team token.
5. publish_slack_message uses the Team/Bot Token (xoxb-...) to DM U12345.

{
  "alert_id": "test_alert_001",
  "platform": "slack",
  "user_id": "1", 
  "title": "Campaign Update",
  "summary": "Hello This is a test notification sent from Vibelets Backend via PostgreSQL lookup!"
}


DEBUG: Checking Slack connection for 1: {'connected': True, 'slack_user_id': 'U0A8LC3ELP8', 'email': 'chandan.kumar@adsparkx.com', 'team_id': 'T0A8NCYDA10', 'team_name': 'Adsparkx', 'bot_user_id': 'U0A9H5GBUNL'}     
INFO:services.slack_service:Team T0A8NCYDA10: Token expires in 46218 seconds.
INFO:services.slack_service:Using team-specific token for team T0A8NCYDA10
INFO:     127.0.0.1:57811 - "POST /bot/notify HTTP/1.1" 200 OK
INFO:     35.153.200.243:0 - "POST /bot/slack/events HTTP/1.1" 200 OK
INFO:services.slack_service:Team T0A8NCYDA10: Token expires in 46207 seconds.
INFO:services.slack_service:Using team-specific token for team T0A8NCYDA10


### Slack logic: "Context-Aware" logic linking Inbound (Flow A) and Outbound (Flow B) communication.

# Flow A: Outbound Notification (services/vibelets_service.py push_notification)
Trigger: An alert is generated in the Vibelets Dashboard.
Action: The backend queries the database to find the connected Slack user.
Context Injection: It retrieves the alert_id and passes it to the resolve_query function.
AI Processing: resolve_query sends this ID to the Vibelets AI Service.
Response: The AI Service generates a concise summary and sends it back to the Slack user via the Slack API.
# Flow B: Inbound Reply (Event) slack_service.py (handle_event) : resolve_query logic
Trigger: The Slack user replies to the bot's message in Slack.
Action: Slack sends an event to the backend.
Context Extraction: The backend parses the event and extracts the thread_ts (timestamp of the original message).
AI Processing: resolve_query is called with the user's reply and the thread_ts.
Response: The AI Service uses the thread_ts to understand the conversation history and generates a relevant follow-up response, which is then sent back to Slack.

### if the chat is out of context then????
If the chat is "out of context" (e.g., the user sends a message like "Hello bot" that is not a reply to an alert, or a reply to a very old alert the AI doesn't remember):

* The System Detects No Thread: in slack_service.py, if "thread_ts" in event: will be false (or the thread will be empty).
* Context is Empty: resolve_query receives context={}.
* Default AI Behavior: The request is sent to the Vibelets AI as a standalone question: {"question": "Hello bot", "context": {}}.
* Line 50-60: It prepares the payload. If context is empty or None, it sends {"user_id": ..., "question": ...}.
* Line 55: It POSTs this standard payload to your Main Vibelets AI Endpoint.

* AI Response: The Vibelets AI treats it as a fresh query. It answers based on general knowledge or real-time dashboard data (e.g., "Hi! I can help you with your campaigns..."), rather than trying to resolve "Fix this".

If is_dummy_request is True (Gemini Mode), the default behavior is in Lines 25-29 (where it just prompts Gemini with the question, adding context only if context exists).


### push_notification
Explanation:
This function acts as a "Broadcast Router". Its job is to take a generic message (Title + Summary) and figure out where to send it for a specific user.

Step-by-Step Logic:

# Input (Payload): It receives a BotNotification object containing:
* user_id(primary key of adu_users): The Vibelets User ID (e.g., "1").  Postgresql_db.py
* platform: Where to send it ("slack", "telegram", or "all").
* title and summary: The message content.

# Discovery (Lines 76-91):
* It checks the platform filter.
* Slack: Calls get_slack_connection(user_id) from the database.
* If the user has linked their Slack account (connected: True), it adds their Slack ID (e.g., U12345) to the targets list.
* Telegram: Calls get_telegram_connection(user_id).
* If linked, adds their Chat ID to the targets list.

# Dispatch (Lines 101-118):
* It loops through the targets list.
* If Slack: It calls slack_send_message (which uses the stored Bot Token to DM the user).
* If Telegram: It calls telegram_send_message.
* It collects the results (e.g., {"slack": "sent", "telegram": "failed"}) and returns them.

Key Benefit: The backend dashboard doesn't need to know what app the user prefers. It just says "Notify User 1", and this service handles the delivery logic.