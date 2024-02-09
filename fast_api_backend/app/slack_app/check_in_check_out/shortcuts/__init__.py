from logging import Logger
from slack_bolt.async_app import AsyncAck, AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from app.database.database import get_db
from app.models.time_sheet import TimeSheet
from app.models.user import User
from app.slack_app.check_in_check_out.views.checkin import get_checkIn_form
from app.slack_app.check_in_check_out.views.checkout import get_checkOut_form
from app.slack_app.profile.views.register import user_registration_form


async def handle_checkIn_shortcut(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    try:
        async with get_db() as db_session:
            await ack()
            slack_id: str = body["user"]["id"]

            user: User | None = await User.get_user_by_slack_id(
                db_session, slack_id=slack_id
            )  # db user object

            # if user is not registered show registration form
            # TODO: add the telegram_id checker here
            if not user:
                await client.views_open(
                    trigger_id=body["trigger_id"],
                    view=await user_registration_form(
                        db_session=db_session,
                    ),
                )
                return

            # Enable it after the announcement
            if user.telegram_id is None:
                await client.views_open(
                    trigger_id=body["trigger_id"],
                    view=await user_registration_form(
                        db_session=db_session,
                        fullname=user.full_name,
                        role=user.role,
                        user=user,
                        is_update=True,
                    ),
                )
                return

            last_check_in: TimeSheet | None = await TimeSheet.get_checkin_stats(
                db_session, slack_id=slack_id
            )

            if last_check_in:
                # if there is a timesheet row that is doesn't have a check out page it means user has already checked int
                await client.views_open(
                    trigger_id=body["trigger_id"],
                    view=get_checkOut_form(user=user, last_check_in=last_check_in),
                )
                return

            await client.views_open(
                trigger_id=body["trigger_id"],
                view=await get_checkIn_form(
                    db_session=db_session,
                    user=user,
                ),
            )
    except Exception as ex:
        logger.error(ex)


def register_shortcuts(app: AsyncApp):
    app.shortcut("test_id")(handle_checkIn_shortcut)
