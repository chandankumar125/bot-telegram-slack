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