from logging import Logger
from slack_bolt.async_app import AsyncAck, AsyncBoltContext, AsyncSay
from slack_sdk.web.async_client import AsyncWebClient
from app.database.database import get_db
from app.models.time_sheet import TimeSheet, get_elapsed_time
from app.models.user import User
from app.slack_app.attachments.check_out_attachment import (
    already_checked_out_attachment,
)
from app.slack_app.check_in_check_out.views.chcek_out_dialog import (
    get_confirmation_dialogOUT,
)
from app.slack_app.check_in_check_out.views.checkout import get_checkOut_form
from app.slack_app.profile.views.register import user_registration_form
from utils import convert_time_to_string, get_current_time


async def handle_checkOut_action(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
    context: AsyncBoltContext,
    say,
):
    async with get_db() as db_session:
        await ack()

        slack_id = body["user"]["id"]
        last_check_in: TimeSheet | None = await TimeSheet.get_checkin_stats(
            db_session, slack_id=slack_id
        )

        user_db_object: User | None = await User.get_user_by_slack_id(
            db_session, slack_id
        )

        if not user_db_object:
            await client.views_open(
                trigger_id=body["trigger_id"],
                view=await user_registration_form(
                    db_session, body["user"]["username"], ""
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

        if not last_check_in:
            await ack()

            await client.chat_postMessage(
                channel=slack_id,
                text="you've already checked-out",
                attachments=already_checked_out_attachment(),
            )
            return
        else:
            await ack()
            await client.views_open(
                trigger_id=body["trigger_id"],
                view=get_checkOut_form(user_db_object, last_check_in),
            )


async def handle_checkOut(
    body: dict,
    logger: Logger,
    ack: AsyncAck,
    say: AsyncSay,
    client: AsyncWebClient,
):
    try:
        async with get_db() as db_session:
            slack_id = body["user"]["id"]

            # get the last checking here
            last_check_in: TimeSheet | None = await TimeSheet.get_checkin_stats(
                db_session=db_session, slack_id=slack_id
            )
            if not last_check_in:
                await ack()
                return
            elasped_time = get_elapsed_time(last_checkin_time=last_check_in)
            check_inTime = last_check_in.check_in_time
            response = await TimeSheet.checkout_operation(
                slack_id=slack_id, db_session=db_session
            )
            if response["success"]:
                response = await client.users_info(user=body["user"]["id"])
                user = response["user"]
                user = await User.get_user_by_slack_id(db_session, slack_id)
                if not user:
                    return
                await ack(
                    response_action="update",
                    view=get_confirmation_dialogOUT(user, elasped_time, check_inTime),
                )
                await say(
                    f"<@{slack_id}> has checked out at {convert_time_to_string(get_current_time())}",
                    channel=user.check_in_check_out_channel,
                )
    except Exception as ex:
        logger.error(ex)
