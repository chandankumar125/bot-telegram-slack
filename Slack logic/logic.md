
###  a restaurant:
# routers/slack.py (The Waiter):
`Router as waiter` receive order(HTTP request) from the customer Slack 
then routers checks `the menu(Schemas)` to make sure the order is valid.
* Correlation: Router uses schemas/slack.py to validate input, calls services/slack_service.py to process it. 
# schemas/vibelets.py (The Menu): 
Role: Defines exactly what data looks like.
Action: "An incoming Slack Event acts like this." "A question to Vibelets looks like that."
Correlation: Used by Router and Services to ensure data integrity.

# The Kitchen - Station Chef for services/slack_service.py:
then (Services) to cook it and serve the order (HTTP response). 
Checks if the user is authorized (asks Utils DB).
If authorized, it needs an answer. It asks the Head Chef (Vibelets Service).
Once it has the answer, it plates it up and asks the Runner (Helpers) to deliver it.
* Correlation: Imports utils/postgres_db (to check user), imports services/vibelets_service (to get AI answer), imports helpers/slack_api (to send reply).

# services/vibelets_service.py (The Head Chef - AI Logic):
Role: The brain. It answers the actual questions.
Action: It takes a question ("How are my ads?"), asks the external Vibelets API (or Gemini), and returns the smart answer.
* Correlation: Used by Services and Routers to read/write connection links.
# utils/postgres_db.py (The Pantry / Inventory):
Role: Stores persistent data.
Action: "Who is Slack User U123?" "Oh, that matches Vibelets User #55." OR "Give me the Access Token for Team T999."
* Correlation: Used by Services and Routers to read/write connection links.
# helpers.py (The Runner - Delivery Service):
Role: Delivers the final result back to the customer.
Action: It takes the prepared response string and physically sends the HTTP POST request back to Slack's servers.
* Correlation: Called by services/slack_service when it's time to talk back.


### The Full Flow (Correlated) of  a restaurant:
Scenario: User sends "Hi" on Slack

1. Slack sends HTTP POST to routers/slack.py.
2. Router validates data using schemas/slack.py.
3. Router calls services/slack_service.py-> handle_event().
4. Service calls utils/postgres_db.py-> get_vibelets_user() to see who this is.
5. Service calls services/vibelets_service.py-> resolve_query("Hi").
6. Vibelets Service returns "Hello! I am Vibelets Bot."
7. Service calls helpers/slack_api.py-> publish_slack_message("Hello...").
8. Helper sends the data back to Slack.
###

{'GET'} /bot/slack/install
{'GET'} /bot/slack/oauth_callback
{'POST'} /bot/slack/disconnect
{'GET'} /bot/slack/status
{'POST'} /bot/slack/events
{'GET'} /bot/slack/events
{'POST'} /bot/telegram/webhook
{'GET'} /bot/telegram/connect
{'POST'} /bot/telegram/disconnect
{'GET'} /bot/telegram/status
{'GET'} /bot/whatsapp/webhook
{'POST'} /bot/whatsapp/webhook
{'GET'} /bot/whatsapp/status
{'POST'} /bot/whatsapp/disconnect
{'GET'} /bot/whatsapp/connect
{'POST'} /bot/notify
{'GET'} /bot/notify
{'GET'} /health

### I have implemented the JWT Authentication Middleware and applied it to your routes.

Summary of Changes:

1. Dependencies: Added PyJWT to requirements.txt.
2. Configuration: Added JWT_SECRET and JWT_ALGORITHM to config.py
3. Middleware/Auth Logic: Created utils/auth.py which contains:
* verify_jwt(authorization): Decodes and validates the Authorization: Bearer <token> header.
* get_current_user(...): A FastAPI dependency that extracts and returns the user_id from the valid token.
4. Secured Routes: I have updated the following endpoints to strictly require a valid JWT. They no longer accept user_id as a query parameter from the URL, but instead extract it securely from the token:
Slack:
GET /bot/slack/status
POST /bot/slack/disconnect
* Why wasn't /bot/slack/install secured with JWT?
The Slack "Connect" flow is fundamentally different from a standard API call:
It's a User Redirect, not an API fetch: When the user clicks "Connect Slack", the browser must fully navigate away from your site to slack.com.
Browsers can't send Headers on Redirects: You cannot attach an Authorization: Bearer header to a standard <a> tag link or a window.location.href navigation.
The Constraint: Slack needs to know who is connecting, but we can't pass the JWT header to Slack's external server.
* How do we secure it then? Currently, we simply pass ?user_id=1 in the URL.

The Risk: A malicious user could theoretically construct a link .../install?user_id=999 and trick an Admin into clicking it, potentially linking the Admin's Slack to User 999's account (this is a CSRF-style attack).
The Solution (Authentication Proxy): Instead of linking directly to /install, the frontend should call a secured API endpoint (e.g., POST /bot/slack/generate-install-link) sending the JWT. The backend validates the JWT, generates a signed short-lived URL or cookie, and returns that safe URL to the frontend to redirect to.

# Important Next Step: Your frontend (app.jsor dashboard) 
must now include the Authorization: Bearer <your_jwt_token> header when calling these endpoints. If it continues to just send ?user_id=1, these requests will fail with 401 Unauthorized or 422 Validation Error.
* I've updated static/js/app.js
 to include the Authorization header with a hardcoded JWT (valid for USER ID 1 and the default secret) in all relevant API calls. Now your frontend will successfully communicate with the secured backend endpoints.

# Option 1: The "Real" Way (Production style) In a real app, 
the authToken would not be hardcoded. It would come from the user logging into your Vibelets Dashboard (e.g., via a Login API that returns a token).
If you had a Login page, you would log in as "User 2", get a token, and the app would use it automatically.

# Option 2: The "Quick Fix" (For Testing) Since you are testing locally and don't have a full login system yet, you can simply change the hardcoded token in 
static/js/app.js to match the token for User 2.

How to get the Token for User 2:
Go to your backend terminal where you ran uvicorn.
Look for the line where it prints the JWT for User 1.
Copy that token.
Paste it into static/js/app.js in place of the User 1 token.
Now your frontend will "pretend" to be User 2 and the backend will accept it.


###

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


###  Slack works in these two scenarios
# Case 1: Individual User
* Action: The user clicks "Add to Slack" and authorizes the app.
* Result: 
We get an access_token for their workspace.
We get their slack_user_id(e.g., U12345).
Your code saves this link: Slack User U12345 = Vibelets User 1.
* Usage: When they chat, the bot sees U12345, looks it up, finds Vibelets User 1, and answers.

# Case 2: Small Business (Multiple Users)
Let's say a company "TechCorp" installs your bot. They have 1 Admin (Alice) and 2 employees (Bob and Charlie).

1. Installation (The "Workspace" Layer)

Alice (Admin) installs the bot.
Slack gives you one access_token for the "TechCorp" workspace.
The bot is now legally allowed to exist in their workspace and speak in channels it is invited to.
Current Code: Alice is now connected (Slack:Alice = Vibelets:Alice), because she performed the installation.
2. Employee Interaction (The "User" Layer)

Bob sends a message to the bot: "Show my stats".
The bot receives an event from Slack saying: "User U_BOB said 'Show my stats'".
Your Code's Check: get_vibelets_user_by_slack_id('U_BOB').
Result: It returns None (Bob hasn't linked his account yet).
Bot Response: It replies to Bob: "⚠️ Account Not Connected. Please 
link your Vibelets account to continue."

3. The Connection Flow (Resolving it)
Bob clicks the link.
He logs into his Vibelets account.
The system creates a new entry in your database: Slack User U_BOB = Vibelets User Bob.
Now Bob can chat with the bot and see logic specific to Bob's Vibelets data.

# Why is it done this way?
This is the standard security model for Slack apps (like Jira, Asana, Linear).

Security: Just because I prefer working in the same Slack workspace as you doesn't mean I should see your private Vibelets dashboard data upon installation.
Personalization: Bob wants to see his campaigns, not Alice's. By forcing individual linking, the bot knows exactly who is asking.

* Alternative: "Shared Account" (Not currently implemented)
If you wanted everyone in the company to access the same Vibelets account without logging in individually, you would have to change your logic to map the Team ID (T12345) to a single Vibelets User, instead of mapping the User ID (U12345). This is common for simple tools (like a "Lunch Choice" bot) but risky for data tools like yours.


###  how the system handles different emails on Vibelets and Slack:

The user CAN use different emails for Vibelets and Slack. They do not need to match.

* How it works:
* Vibelets Identity: The user is logged into the Vibelets Dashboard with personal@gmail.com. This gives them User ID: 1.
* Slack Identity: The user uses work@company.com on Slack.
* The Linking Process:
The user clicks "Connect Slack" from inside the Vibelets Dashboard.
This sends their User ID 1 to the Slack authorization page.
When they authorize Slack (as work@company.com), your backend receives Slack User ID (e.g., U123) and links it to Vibelets User ID 1.
* Result:
In your database: User 1 maps to Slack User U123.
The emails (personal@gmail.com vs work@company.com) are irrelevant for the connection itself. The link is established via the secure OAuth handshake, not by matching email strings.



