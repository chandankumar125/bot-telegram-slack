Vibelets.ai Alert Engine
        │
        ▼
FastAPI Bot Backend
        │
 ┌──────┴─────────┐
 ▼                ▼
Telegram Bot     Slack App



.\ngrok.exe http 8000    ------
uvicorn main:app --reload --port 8000 
python check_bot_setup.py 
python send_test_notification.py C0A8LGRCGT0 "Server Alert" "Welcome to Vibelets"  

https://core.telegram.org/bots/api



t.me/Vibelets_bot. 
telegram- search @Botfather
user id- seard Bot id
/start
/mybots

python send_test_notification_telegram.py 5530989549 "Server Alert" "your ads impression  are too low  . Be alert!"
uvicorn main:app --reload --port 8000
 .\ngrok.exe http 8000    

# whatsApp:
1️⃣ WhatsApp Product Added
App created in Meta
WhatsApp product enabled
✔️ You already did this
2️⃣ Phone Number ID
Test number (for learning) OR
Real number (for production)
✔️ You already have Phone Number ID
3️⃣ Access Token
Temporary → OK for testing
Permanent → REQUIRED for real bot
✔️ Temp works
❌ Permanent needed for real bot
4️⃣ Webhook (THIS IS NON-NEGOTIABLE)
Without webhook:
You cannot receive user messages
Bot cannot auto-reply
Required:
Callback URL
Verify Token
/webhook endpoint in backend
➡️ This is the core of a bot