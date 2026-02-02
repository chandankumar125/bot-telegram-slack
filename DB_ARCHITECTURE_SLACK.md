# Slack Integration - Database Architecture

This document defines the PostgreSQL database schema for Slack integration with the Vibelets platform.

---

## Existing Table (No Changes)
# You need adu_users id to know whose data to show.
```sql
-- Your existing table (unchanged)
adu_users (
    id,
    email,
    first_name,
    created_at
)
```

---

## New Tables for Slack Integration

### TABLE 1: Slack Workspaces (Team-level data)

Stores ONE record per Slack workspace that installs your app.
Tokens are stored here (shared by all users in the workspace).

```sql
CREATE TABLE slack_workspaces (
    id                  SERIAL PRIMARY KEY,
    team_id             VARCHAR(50) UNIQUE NOT NULL,  -- Slack's team ID (e.g., "T0A8XXXX")
    team_name           VARCHAR(255),
    
    -- Bot credentials
    bot_user_id         VARCHAR(50),                   -- Bot's user ID in this workspace
    access_token        TEXT NOT NULL,                 -- Bot OAuth token (encrypted in production)
    
    -- Token rotation fields (nullable for non-rotating tokens)
    refresh_token       TEXT,
    token_expires_at    TIMESTAMP WITH TIME ZONE,
    
    -- Metadata
    installed_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active           BOOLEAN DEFAULT TRUE           -- Set FALSE when app uninstalled
);

CREATE INDEX idx_slack_workspaces_team_id ON slack_workspaces(team_id);
```

---

### TABLE 2: Slack User Connections (User-level data)

Links YOUR users (adu_users) to their Slack accounts.
Many users can belong to the same workspace.

```sql
CREATE TABLE slack_user_connections (
    id                  SERIAL PRIMARY KEY,
    
    -- Link to your existing users table
    user_id             INTEGER NOT NULL REFERENCES adu_users(id) ON DELETE CASCADE,
    
    -- Link to workspace
    workspace_id        INTEGER NOT NULL REFERENCES slack_workspaces(id) ON DELETE CASCADE,
    
    -- Slack user info
    slack_user_id       VARCHAR(50) NOT NULL,          -- Slack's user ID (e.g., "U0A8YYYY")
    slack_email         VARCHAR(255),
    slack_username      VARCHAR(255),
    slack_display_name  VARCHAR(255),
    
    -- Connection status
    connected_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    disconnected_at     TIMESTAMP WITH TIME ZONE,      -- NULL if still connected
    is_connected        BOOLEAN DEFAULT TRUE,
    
    -- Constraints
    UNIQUE(user_id),                                   -- One Slack connection per user
    UNIQUE(slack_user_id)                              -- One user per Slack account
);

CREATE INDEX idx_slack_user_connections_user_id ON slack_user_connections(user_id);
CREATE INDEX idx_slack_user_connections_slack_user_id ON slack_user_connections(slack_user_id);
CREATE INDEX idx_slack_user_connections_workspace_id ON slack_user_connections(workspace_id);
```

---

### TABLE 3: Slack Event Log (Optional - for audit/debugging)

Tracks events for deduplication and debugging.

```sql
CREATE TABLE slack_event_logs (
    id                  SERIAL PRIMARY KEY,
    event_id            VARCHAR(100) UNIQUE,           -- Slack's event ID (for deduplication)
    team_id             VARCHAR(50) NOT NULL,
    event_type          VARCHAR(50) NOT NULL,          -- "message", "app_mention", etc.
    user_id             VARCHAR(50),                   -- Slack user who triggered
    channel_id          VARCHAR(50),
    event_payload       JSONB,                         -- Full event for debugging
    processed_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Expire old logs automatically (optional)
    expires_at          TIMESTAMP WITH TIME ZONE DEFAULT (NOW() + INTERVAL '30 days')
);

CREATE INDEX idx_slack_event_logs_event_id ON slack_event_logs(event_id);
CREATE INDEX idx_slack_event_logs_team_id ON slack_event_logs(team_id);
```

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         EXISTING TABLE                                  │
│  ┌─────────────────┐                                                    │
│  │   adu_users     │                                                    │
│  ├─────────────────┤                                                    │
│  │ id (PK)         │◄─────────────────────────┐                         │
│  │ email           │                          │                         │
│  │ first_name      │                          │                         │
│  │ created_at      │                          │                         │
│  └─────────────────┘                          │                         │
└───────────────────────────────────────────────┼─────────────────────────┘
                                                │
┌───────────────────────────────────────────────┼─────────────────────────┐
│                      NEW TABLES               │                         │
│                                               │                         │
│  ┌─────────────────────────┐    ┌─────────────┴─────────────┐          │
│  │   slack_workspaces      │    │  slack_user_connections   │          │
│  ├─────────────────────────┤    ├───────────────────────────┤          │
│  │ id (PK)                 │◄───┤ workspace_id (FK)         │          │
│  │ team_id (UNIQUE)        │    │ user_id (FK) ─────────────┘          │
│  │ team_name               │    │ id (PK)                              │
│  │ bot_user_id             │    │ slack_user_id (UNIQUE)               │
│  │ access_token            │    │ slack_email                          │
│  │ refresh_token           │    │ slack_username                       │
│  │ token_expires_at        │    │ is_connected                         │
│  │ is_active               │    │ connected_at                         │
│  │ installed_at            │    │ disconnected_at                      │
│  │ updated_at              │    └───────────────────────────┘          │
│  └─────────────────────────┘                                           │
│                                                                         │
│  ┌─────────────────────────┐                                           │
│  │   slack_event_logs      │  (Optional - for audit)                   │
│  ├─────────────────────────┤                                           │
│  │ id (PK)                 │                                           │
│  │ event_id (UNIQUE)       │                                           │
│  │ team_id                 │                                           │
│  │ event_type              │                                           │
│  │ event_payload (JSONB)   │                                           │
│  │ processed_at            │                                           │
│  └─────────────────────────┘                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Common Queries

### 1. Save new Slack connection (OAuth callback)

```sql
-- Step 1: Insert or update workspace
INSERT INTO slack_workspaces (team_id, team_name, bot_user_id, access_token, refresh_token, token_expires_at)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT (team_id) 
DO UPDATE SET 
    access_token = EXCLUDED.access_token,
    refresh_token = EXCLUDED.refresh_token,
    token_expires_at = EXCLUDED.token_expires_at,
    updated_at = NOW(),
    is_active = TRUE
RETURNING id;

-- Step 2: Link user to workspace
INSERT INTO slack_user_connections (user_id, workspace_id, slack_user_id, slack_email)
VALUES ($1, $2, $3, $4)
ON CONFLICT (user_id) 
DO UPDATE SET 
    workspace_id = EXCLUDED.workspace_id,
    slack_user_id = EXCLUDED.slack_user_id,
    slack_email = EXCLUDED.slack_email,
    is_connected = TRUE,
    connected_at = NOW(),
    disconnected_at = NULL;
```

### 2. Get token for a team (when processing events)

```sql
SELECT access_token, refresh_token, token_expires_at
FROM slack_workspaces
WHERE team_id = $1 AND is_active = TRUE;
```

### 3. Find user by Slack ID (for event handling)

```sql
SELECT 
    u.id AS user_id,
    u.email,
    u.first_name,
    suc.slack_user_id,
    sw.team_id,
    sw.access_token
FROM slack_user_connections suc
JOIN adu_users u ON u.id = suc.user_id
JOIN slack_workspaces sw ON sw.id = suc.workspace_id
WHERE suc.slack_user_id = $1 AND suc.is_connected = TRUE;
```

### 4. Check connection status

```sql
SELECT 
    suc.is_connected,
    sw.team_name,
    suc.slack_email,
    suc.connected_at
FROM slack_user_connections suc
JOIN slack_workspaces sw ON sw.id = suc.workspace_id
WHERE suc.user_id = $1;
```

### 5. Disconnect user

```sql
UPDATE slack_user_connections
SET is_connected = FALSE, disconnected_at = NOW()
WHERE user_id = $1;
```

### 6. Refresh token update

```sql
UPDATE slack_workspaces
SET 
    access_token = $2,
    refresh_token = $3,
    token_expires_at = $4,
    updated_at = NOW()
WHERE team_id = $1;
```

---

## Key Design Decisions

| Decision | Reasoning |
|----------|-----------|
| **Separate workspace & user tables** | Tokens are per-workspace, users are per-person |
| **Soft delete (is_connected)** | Preserve history, easy reconnection |
| **Foreign key to adu_users** | Clean referential integrity |
| **UNIQUE on slack_user_id** | Prevents one Slack account linking to multiple users |
| **Event logs table** | Enables deduplication & debugging |
| **JSONB for event_payload** | Flexible storage for varying event types |

---

## Future Extensibility

For Telegram & WhatsApp, follow the same pattern:

### Telegram (no workspace concept, simpler)

```sql
CREATE TABLE telegram_user_connections (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES adu_users(id) ON DELETE CASCADE,
    chat_id             VARCHAR(50) NOT NULL UNIQUE,
    username            VARCHAR(255),
    first_name          VARCHAR(255),
    last_name           VARCHAR(255),
    connected_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    disconnected_at     TIMESTAMP WITH TIME ZONE,
    is_connected        BOOLEAN DEFAULT TRUE,
    
    UNIQUE(user_id)
);
```

### WhatsApp

```sql
CREATE TABLE whatsapp_user_connections (
    id                  SERIAL PRIMARY KEY,
    user_id             INTEGER NOT NULL REFERENCES adu_users(id) ON DELETE CASCADE,
    whatsapp_id         VARCHAR(50) NOT NULL UNIQUE,
    phone_number        VARCHAR(20),
    display_name        VARCHAR(255),
    connected_at        TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    disconnected_at     TIMESTAMP WITH TIME ZONE,
    is_connected        BOOLEAN DEFAULT TRUE,
    
    UNIQUE(user_id)
);
```

---

## Data Flow Summary

```
1. OAuth Connect:
   User clicks "Connect Slack" 
   → Slack OAuth 
   → Callback with code 
   → Exchange for token 
   → INSERT into slack_workspaces 
   → INSERT into slack_user_connections

2. Event Processing:
   Slack sends event 
   → Extract team_id 
   → SELECT token from slack_workspaces 
   → Extract slack_user_id 
   → SELECT user_id from slack_user_connections 
   → Process & reply

3. Disconnect:
   User clicks "Disconnect" 
   → UPDATE slack_user_connections SET is_connected = FALSE
   → (Token remains for other users in same workspace)
```
