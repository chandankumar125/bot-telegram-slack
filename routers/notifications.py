from fastapi import APIRouter
from schemas.vibelets import BotNotification
from services.vibelets_service import push_notification

router = APIRouter()

@router.post("/notify")
def notify(payload: BotNotification):
    return push_notification(payload)

@router.get("/notify")
def notify_info():
    return {"ok": True}
