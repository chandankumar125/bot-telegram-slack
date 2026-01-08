from fastapi import FastAPI
from telegram import telegram_webhook
from slack import slack_events

app = FastAPI()

app.post("/bot/telegram/webhook")(telegram_webhook)
app.post("/bot/slack/events")(slack_events)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
