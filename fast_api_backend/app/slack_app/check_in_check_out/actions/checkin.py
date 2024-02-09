from logging import Logger
from slack_bolt.async_app import AsyncAck, AsyncBoltContext, AsyncSay
from slack_sdk.web.async_client import AsyncWebClient
from app.database.database import get_db
from app.models.time_sheet import TimeSheet
from app.models.user import User
from app.slack_app.attachments.check_in_attachment import already_checked_in_attachment
from app.slack_app.check_in_check_out.views.check_in_dialog import (
    get_confirmation_dialog,
)
from app.slack_app.check_in_check_out.views.checkin import get_checkIn_form
from app.slack_app.profile.views.register import user_registration_form
from utils import convert_time_to_string, get_current_time


async def handle_checkIn_action(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
    context: AsyncBoltContext,
):
    async with get_db() as db_session:
        await ack()

        slack_id = body["user"]["id"]

        await ack()
        user_db_object: User | None = await User.get_user_by_slack_id(
            db_session, slack_id
        )

        if not user_db_object:
            await client.views_open(
                trigger_id=body["trigger_id"],
                view=await user_registration_form(
                    db_session=db_session,
                    fullname=body["user"]["username"],
                    role="",
                ),
            )
            return
        await ack()

        # Enable it after the announcement
        if user_db_object.telegram_id is None:
            await client.views_open(
                trigger_id=body["trigger_id"],
                view=await user_registration_form(
                    db_session=db_session,
                    fullname=user_db_object.full_name,
                    role=user_db_object.role,
                    user=user_db_object,
                    is_update=True,
                ),
            )
            return

        if await TimeSheet.get_checkin_stats(db_session, slack_id):
            await ack()

            await client.chat_postMessage(
                channel=slack_id,
                text="you've already checked in",
                attachments=already_checked_in_attachment(),
            )

        else:
            await ack()

            await client.views_open(
                trigger_id=body["trigger_id"],
                view=await get_checkIn_form(
                    db_session=db_session,
                    user=user_db_object,
                ),
            )


async def handle_checkIn(
    body: dict,
    ack: AsyncAck,
    logger: Logger,
    say: AsyncSay,
):
    try:
        async with get_db() as db_session:
            project = body["view"]["state"]["values"]["check-in_menu_select_project"][
                "static_select-action"
            ]["selected_option"]["value"]
            location = body["view"]["state"]["values"][
                "check-in_menu_select_working_location"
            ]["selected_working_location-action"]["selected_option"]["value"]

            response = await TimeSheet.checkin_operation(
                db_session, body["user"]["id"], project, location
            )

            if response["success"]:
                user = await User.get_user_by_slack_id(db_session, body["user"]["id"])
                if not user:
                    return
                await ack(
                    response_action="update", view=get_confirmation_dialog(user=user)
                )
                await say(
                    f"<@{body['user']['id']}> has checked-in {'Remotely' if location == 'Remote' else 'In-Person'}{(' at ' + location.split(' ')[0]) if location != 'Remote' else ''} at {convert_time_to_string(get_current_time())}",
                    channel=user.check_in_check_out_channel,
                )
    except Exception as ex:
        logger.error(ex)
