from fastapi import BackgroundTasks
from slack_sdk.models.attachments import Attachment
from sqlalchemy.ext.asyncio import AsyncSession
from app.constants import AttachmentColors, ButtonTypes
from app.slack_app import SlackAppInstance
from app.slack_app.attachments.check_in_attachment import attachmet_create
from app.slack_app.notifications.logics import (
    get_users_who_havent_checkedin,
    get_users_who_havent_checkedout,
)
from app.telegram_bot import (
    send_checkin_reminder_message,
    send_checkout_reminder_message,
)
from config import MySettings


API_URL: str = MySettings.API_URL


async def send_morning_check_in_message(
    db_session: AsyncSession, worker: BackgroundTasks
):
    header_message = "This is your morning check in reminder"
    body_message = "Good morning! It's time to start your day and log your attendance. Please click the 'Check-In' button to record your arrival."

    # filter people that haven't checked in so far
    users = await get_users_who_havent_checkedin(db_session)
    for user in users:
        attachments: list[Attachment] = attachmet_create(
            slack_id=user.slack_id,
            header_message=header_message,
            body_message=body_message,
            attachment_color=AttachmentColors["green"],
            image_url=f"{API_URL}/static/check_in.png",
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


async def send_lunch_break_checkout_message(
    db_session: AsyncSession,
    worker: BackgroundTasks,
):
    header_message = "This is your lunch break Reminder"
    body_message = "It's time for your lunch break. Don't forget to check out and log your departure. Please click the 'Check-Out' button to record your lunch break."

    users = await get_users_who_havent_checkedout(db_session)
    for user in users:
        attachments: list[Attachment] = attachmet_create(
            slack_id=user.slack_id,
            header_message=header_message,
            body_message=body_message,
            attachment_color=AttachmentColors["red"],
            image_url=f"{API_URL}/static/check_out.png",
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


async def send_afternoon_check_in_message(
    db_session: AsyncSession,
    worker: BackgroundTasks,
):
    header_message = "This is your afternoon check in reminder"
    body_message = "The afternoon session is about to begin. Please click the 'Check-In' button to record your return."

    users = await get_users_who_havent_checkedin(db_session)

    for user in users:
        attachments: list[Attachment] = attachmet_create(
            slack_id=user.slack_id,
            header_message=header_message,
            body_message=body_message,
            attachment_color=AttachmentColors["green"],
            image_url=f"{API_URL}/static/check_in.png",
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


async def send_final_checkout_message(
    db_session: AsyncSession,
    worker: BackgroundTasks,
):
    header_message = "This is your afternoon check out reminder"
    body_message = "The workday is coming to an end. Don't forget to check out and log your departure. Please click the 'Check-Out' button to record your checkout."
    users = await get_users_who_havent_checkedout(db_session)

    for user in users:
        attachments: list[Attachment] = attachmet_create(
            slack_id=user.slack_id,
            header_message=header_message,
            body_message=body_message,
            attachment_color=AttachmentColors["red"],
            image_url=f"{API_URL}/static/check_out.png",
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
