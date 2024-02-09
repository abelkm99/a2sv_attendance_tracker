from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db_router
from app.slack_app.notifications.notification import (
    send_morning_check_in_message,
    send_lunch_break_checkout_message,
    send_afternoon_check_in_message,
    send_final_checkout_message,
)


from enum import Enum

from app.router.api_v1.notification.services import (
    user_list_getter_services,
)


class NotificationType(str, Enum):
    MORNING_CHECK_IN = "MORNING_CHECK_IN"
    MORNING_CHECK_OUT = "MORNING_CHECK_OUT"
    AFTERNOON_CHECK_IN = "AFTERNOON_CHECK_IN"
    AFTERNOON_CHECK_OUT = "AFTERNOON_CHECK_OUT"


notification_router = APIRouter(
    prefix="/notification",
    tags=["notification"],
    responses={404: {"description": "Not found"}},
)


# FIXME: delete this route
@notification_router.get("/send")
async def get_interval(
    notification_type: NotificationType,
    worker: BackgroundTasks,
    db_session: AsyncSession = Depends(get_db_router),
):
    if notification_type == NotificationType.MORNING_CHECK_IN:
        await send_morning_check_in_message(
            db_session=db_session,
            worker=worker,
        )
        pass
    elif notification_type == NotificationType.MORNING_CHECK_OUT:
        await send_lunch_break_checkout_message(
            db_session=db_session,
            worker=worker,
        )
        pass
    elif notification_type == NotificationType.AFTERNOON_CHECK_IN:
        await send_afternoon_check_in_message(
            db_session=db_session,
            worker=worker,
        )
        pass
    elif notification_type == NotificationType.AFTERNOON_CHECK_OUT:
        await send_final_checkout_message(
            db_session=db_session,
            worker=worker,
        )
        pass

    return "send notification"


@notification_router.get("/send_notification")
async def send_checkin_notification(
    worker: BackgroundTasks,
    slack_app_token: str = Header(None),
    db_session: AsyncSession = Depends(get_db_router),
):
    from config import MySettings

    if slack_app_token != MySettings.SLACK_BOT_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    # get the result from the database
    return await user_list_getter_services(db_session, worker)
