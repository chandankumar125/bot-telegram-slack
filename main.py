from fastapi import FastAPI
from routers import telegram, slack, notifications

app = FastAPI(title="Vibelets Bot Service")

app.include_router(telegram.router, prefix="/bot/telegram")
app.include_router(slack.router, prefix="/bot/slack")
app.include_router(notifications.router, prefix="/bot")

@app.get("/health")
def health():
    return {"status": "ok"}
