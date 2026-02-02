### Data base relationships: 
1. adu_users (The Master List): This is your Real User. If this table didn't exist, you wouldn't have "users," just strangers. You need this to know whose data to show.
2. slack_workspaces (The Permission): This stores functionality for the Company. "TechCorp gave us permission to send messages." It holds the API Token.
3. slack_user_connections (The Link): This bridges the two. "Slack User Bob IS Vibelets User 

ID: 5."
The Flow:
User asks Q on Slack →
Bot checks Link Table to find "ID: 5" →
Bot checks Master List (via ID 5) to get data →
Bot uses Workspace Table Token to reply.


### Data base Schemas: 
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

2️⃣ slack_user_connections table: The "Foreign Key" Relationship for workspace and adu_user

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

### utils/postgres_db.py
contains all the SQL logic for the application, specifically handling the Slack integration.

Here is the breakdown of its key functions:

1. 
save_slack_connection(...)
Goal: Registers a new install. 
Action:
Saves the Company info (Team ID, Name, Token) into slack_workspaces.
Saves the User link (Slack ID ↔ Vibelets ID) into slack_user_connections.
2. 
get_slack_connection(user_id)
Goal: Checks "Is this Vibelets User (ID: 5) connected to Slack?" 
Action:
Looks up slack_user_connections for User 5.
Returns their Slack details (Team Name, Email, Slack ID) if found.
3. 
get_vibelets_user_by_slack_id(slack_user_id)
Goal: Reverse lookup. "Who is Slack User U123?" 
Action:
Used when a message arrives from Slack.
Returns the Vibelets 
user_id
 so the bot knows whose data to fetch.
4. 
get_connection_by_slack_user_id(slack_user_id)
Goal: "I need to send a DM to U123. Which token do I use?" 
Action:
Used for notifications.
Finds the user, checks which Workspace they belong to, and returns that Workspace's access_token.
5. 
disconnect_slack_connection(user_id)
Goal: Unlinks the user. 
Action: Sets is_connected = FALSE in the database. It does not delete the row (allows for history/audit), just deactivates it.

6. get_team_token/ update_team_token
Goal: Internal token management. 
Action: Fetches the raw token for API calls or updates it if it was refreshed.



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

