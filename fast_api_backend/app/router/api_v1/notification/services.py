from datetime import datetime
from enum import Enum
from fastapi import BackgroundTasks
from slack_sdk.models.attachments import Attachment
from sqlalchemy import text

from sqlalchemy.ext.asyncio import AsyncSession
from app.constants import AttachmentColors, ButtonTypes

from app.router.api_v1.notification.schema import SlackUser
from app.slack_app import SlackAppInstance
from app.slack_app.attachments.check_in_attachment import attachmet_create
from app.telegram_bot import (
    send_checkin_reminder_message,
    send_checkout_reminder_message,
)
from config import MySettings


class NotificationType2(str, Enum):
    CHECKIN = "checkin"
    CHECKOUT = "checkout"


def get_statement(
    notification_type: NotificationType2,
):
    has_checkd_in: int = 0 if notification_type == NotificationType2.CHECKIN else 1
    current_time = datetime.utcnow().strftime("%H:%M")
    # print(current_time)

    stmt = f"""
select
	slack_id,
	telegram_id,
	checked_in,
    full_name
from
  (
    select
      users.slack_id,
      users.full_name,
      users.telegram_id,
      sum(
        case when ts.check_in_time >= CAST(
          DATE_TRUNC('day', current_date) AS TIMESTAMP
        )
        AND ts.check_out_time IS null then 1 else 0 end
      ) as checked_in
    from
      (
        select
          slack_id,
          full_name,
          telegram_id
        FROM
          (
            select
              u.full_name,
              u.telegram_id,
              r.slack_id,
              r.notification_type,
              r.id as reminder_id,
              current_date + r.reminder_time as normal_time,
              u.timezone,
              (
                (current_date + r.reminder_time) AT TIME ZONE u.timezone
              ) AT TIME ZONE 'UTC' AS start_time,
              (
                (current_date + r.reminder_time) AT TIME ZONE u.timezone + INTERVAL '1 hour'
              ) AT TIME ZONE 'UTC' AS end_time
            FROM
              public.reminder AS r
              JOIN public."user" u ON u.slack_id = r.slack_id
            where r.notification_type = '{notification_type.value}'
          ) AS calculated_times
        where
          start_time <= start_time::date + '{current_time}'::time
          and end_time::date +  '{current_time}'::time < end_time
        group by
          slack_id,
          full_name,
          telegram_id
        order by
          full_name
      ) as users
      join time_sheet ts on ts.slack_id = users.slack_id
    group by
      users.slack_id,
      users.full_name,
      users.telegram_id
  ) as result
where checked_in = {has_checkd_in}
    """
    return stmt


async def get_checkin_reminder_list(db_session: AsyncSession):
    checkin_reminder_list: list[SlackUser] = []
    stmt = get_statement(NotificationType2.CHECKIN)
    res = await db_session.execute(text(stmt))
    for row in res:
        checkin_reminder_list.append(
            SlackUser(
                slack_id=row.slack_id,
                telegram_id=row.telegram_id,
                full_name=row.full_name,
            )
        )
    # forward it to a task that would send a check in notification
    return checkin_reminder_list


async def get_checkout_reminder_list(db_session: AsyncSession):
    checkout_reminder_list: list[SlackUser] = []
    stmt = get_statement(NotificationType2.CHECKOUT)
    res = await db_session.execute(text(stmt))
    for row in res:
        checkout_reminder_list.append(
            SlackUser(
                slack_id=row.slack_id,
                telegram_id=row.telegram_id,
                full_name=row.full_name,
            )
        )
    # forward it to a task that would send a check in notification
    return checkout_reminder_list


async def send_checkin_notification_service(
    worker: BackgroundTasks,
    users: list[SlackUser],
):
    from app.slack_app import SlackAppInstance

    header_message = "This is your check in reminder"
    body_message = "It's time to start your day and log your attendance. Please click the 'Check-In' button to record your arrival."

    # filter people that haven't checked in so far
    for user in users:
        attachments: list[Attachment] = attachmet_create(
            slack_id=user.slack_id,
            header_message=header_message,
            body_message=body_message,
            attachment_color=AttachmentColors["green"],
            image_url=f"{MySettings.API_URL}/static/check_in.png",
            button_option=True,
            action_id="check_in_reminder_attachment_button",
            button_name="Check-In",
            button_color=ButtonTypes["green"],
        )
        worker.add_task(
            SlackAppInstance.client.chat_postMessage,
            channel=user.slack_id,
            text=header_message,
            attachments=attachments,
        )
        if user.telegram_id:
            worker.add_task(
                send_checkin_reminder_message, user.telegram_id, user.full_name
            )


async def send_checkout_notification(
    worker: BackgroundTasks,
    users: list[SlackUser],
):
    header_message = "This is your check out reminder"
    body_message = "Don't forget to check out and log your departure. Please click the 'Check-Out' button to record your checkout."

    # filter people that haven't checked in so far
    for user in users:
        attachments: list[Attachment] = attachmet_create(
            slack_id=user.slack_id,
            header_message=header_message,
            body_message=body_message,
            attachment_color=AttachmentColors["red"],
            image_url=f"{MySettings.API_URL}/static/check_out.png",
            button_option=True,
            action_id="check_out_reminder_attachment_button",
            button_name="Check-Out",
            button_color=ButtonTypes["red"],
        )
        worker.add_task(
            SlackAppInstance.client.chat_postMessage,
            channel=user.slack_id,
            text=header_message,
            attachments=attachments,
        )
        if user.telegram_id:
            worker.add_task(
                send_checkout_reminder_message, user.telegram_id, user.full_name
            )


async def user_list_getter_services(
    db_session: AsyncSession,
    worker: BackgroundTasks,
) -> dict:
    checkin_reminder_list: list[SlackUser] = await get_checkin_reminder_list(db_session)
    checkout_reminder_list: list[SlackUser] = await get_checkout_reminder_list(
        db_session
    )
    # print("cehckint", checkin_reminder_list)
    # print("checkout", checkout_reminder_list)
    await send_checkin_notification_service(worker, checkin_reminder_list)
    await send_checkout_notification(worker, checkout_reminder_list)
    # forward it to a task that would send a check in notification
    return {"status": True, "detail": "Notification sent successfully"}


async def send_notification_serive():
    pass
