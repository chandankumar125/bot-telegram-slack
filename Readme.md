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