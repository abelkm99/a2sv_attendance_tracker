from datetime import datetime, time
from logging import Logger
from slack_bolt.async_app import AsyncAck, AsyncApp
from slack_sdk.models.attachments import BlockAttachment
from slack_sdk.models.blocks import (
    ButtonElement,
    MarkdownTextObject,
    PlainTextObject,
    SectionBlock,
)
from slack_sdk.web.async_client import AsyncWebClient
from app.database.database import get_db
from app.models.user import Reminder


def convert_to_24_hour_format(time_str: str) -> time:
    try:
        time_str = time_str.strip()
        time_str = time_str.lower()
        # Check if the input is in 12-hour or 24-hour format
        if " " in time_str:
            time_12h = datetime.strptime(time_str, "%I:%M %p")
        else:
            if "am" in time_str or "pm" in time_str:
                time_12h = datetime.strptime(time_str, "%I:%M%p")
            else:
                time_12h = datetime.strptime(time_str, "%H:%M")

        time_24h = time_12h.strftime("%H:%M")

        current_time = datetime.strptime(time_24h, "%H:%M")
        return time(current_time.hour, current_time.minute)
    except Exception as e:
        raise e


async def handle_add_checkin_reminder(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    await ack()
    logger.critical(body)
    given_time = body["text"]
    slack_id = body["user_id"]
    try:
        new_format = convert_to_24_hour_format(given_time)
        async with get_db() as db_session:
            _ = await Reminder.create_new_reminder(
                db_session=db_session,
                reminder_time=new_format,
                notification_type="checkin",
                slack_id=slack_id,
            )
            await client.chat_postEphemeral(
                channel=body["channel_id"],
                user=slack_id,
                text=f"reminder set for {given_time}(12hrs) or {new_format}(24 hrs)",
            )

    except Exception as e:
        await client.chat_postEphemeral(
            channel=body["channel_id"],
            user=slack_id,
            text=f"Error: {e}",
        )
        return


async def handle_add_checkout_reminder(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    await ack()
    given_time = body["text"]
    slack_id = body["user_id"]
    try:
        new_format = convert_to_24_hour_format(given_time)
        async with get_db() as db_session:
            _ = await Reminder.create_new_reminder(
                db_session=db_session,
                reminder_time=new_format,
                notification_type="checkout",
                slack_id=slack_id,
            )
            await client.chat_postEphemeral(
                channel=body["channel_id"],
                user=slack_id,
                text=f"reminder set for {given_time}(12hrs) or {new_format}(24 hrs)",
            )

    except Exception as e:
        await client.chat_postEphemeral(
            channel=body["channel_id"],
            user=slack_id,
            text=f"Error: {e}",
        )
        logger.error(e)
        return


async def handle_remove_reminder(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    await ack()
    given_time = body["text"]
    slack_id = body["user_id"]
    try:
        new_format = convert_to_24_hour_format(given_time)
        async with get_db() as db_session:
            _ = await Reminder.remove_reminder(
                db_session=db_session,
                reminder_time=new_format,
                slack_id=slack_id,
            )
            await client.chat_postEphemeral(
                channel=body["channel_id"],
                user=slack_id,
                text=f"reminder at {given_time}(12hrs) or {new_format}(24 hrs) is now removed",
            )

    except Exception as e:
        await client.chat_postEphemeral(
            channel=body["channel_id"],
            user=slack_id,
            text=f"Error: {e}",
        )
        logger.error(e)
        return

    pass


async def handler_remove_reminder_from_button(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    await ack()
    slack_id = body["user"]["id"]
    block_id = body["actions"][0]["block_id"]
    reminder_time = time.fromisoformat(block_id)
    try:
        async with get_db() as db_session:
            _ = await Reminder.remove_reminder(
                db_session=db_session,
                reminder_time=reminder_time,
                slack_id=slack_id,
            )
            await client.chat_postEphemeral(
                channel=body["container"]["channel_id"],
                user=slack_id,
                text=f"reminder at {reminder_time.strftime('%I:%M %p')}(12hrs) or {reminder_time}(24 hrs) is now removed",
            )
    except Exception as e:
        await client.chat_postEphemeral(
            channel=body["container"]["channel_id"],
            user=slack_id,
            text=f"Error: {e}",
        )
        logger.error(e)
        return

    pass


async def handle_clear_reminders(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    await ack()
    slack_id = body["user_id"]
    try:
        async with get_db() as db_session:
            _ = await Reminder.clear_all_reminders(
                db_session=db_session,
                slack_id=slack_id,
            )
            await client.chat_postEphemeral(
                channel=body["channel_id"],
                user=slack_id,
                text="All reminders are now removed!!",
            )

    except Exception as e:
        await client.chat_postEphemeral(
            channel=body["channel_id"],
            user=slack_id,
            text=f"Error: {e}",
        )
        logger.error(e)
        return

    pass


def get_block_attachments(rm: Reminder):
    return BlockAttachment(
        color="warning",
        blocks=[
            SectionBlock(
                text=MarkdownTextObject(
                    text=f"*{rm.notification_type.upper()} reminder at   :-  {rm.reminder_time.strftime('%I:%M %p')}*"
                ),
                accessory=ButtonElement(
                    text=PlainTextObject(text="delete", emoji=True),
                    action_id="remove_reminder",
                    style="danger",
                ),
                block_id=str(rm.reminder_time),
            )
        ],
    )


async def get_all_reminders(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    await ack()
    slack_id = body["user_id"]
    try:
        attachments = []

        async with get_db() as db_session:
            reminders = await Reminder.get_all_reminders(
                db_session=db_session,
                slack_id=slack_id,
            )
            for reminder in reminders:
                attachments.append(get_block_attachments(reminder))

        _ = await client.chat_postEphemeral(
            channel=body["channel_id"],
            user=slack_id,
            text="Here are all the reminders"
            if len(attachments) > 0
            else "No reminders found",
            attachments=attachments,
        )
    except Exception as e:
        await client.chat_postEphemeral(
            channel=body["channel_id"],
            user=slack_id,
            text=f"Error: {e}",
        )
        logger.error(e)
        return


def register_commands(bot: AsyncApp):
    bot.command("/reminders")(get_all_reminders)
    bot.command("/clear-reminders")(handle_clear_reminders)
    bot.command("/add-checkin-reminder")(handle_add_checkin_reminder)
    bot.command("/add-checkout-reminder")(handle_add_checkout_reminder)
    bot.command("/remove-reminder")(handle_remove_reminder)
    bot.action("remove_reminder")(handler_remove_reminder_from_button)
    pass
