from logging import Logger
from slack_bolt.async_app import AsyncAck, AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from app.database.database import get_db
from app.models.user import User
from app.slack_app.profile.views.register import user_registration_form


async def handle_project_shorcut(
    ack: AsyncAck,
    shortcut: dict,
    logger: Logger,
    client: AsyncWebClient,
    body: dict,
):
    await ack()
    async with get_db() as db_session:
        await ack()
        slack_id = shortcut["user"]["id"]
        user: User | None = await User.get_user_with_project(
            db_session=db_session, slack_id=slack_id
        )
        if user:
            await client.views_open(
                trigger_id=body["trigger_id"],
                view=await user_registration_form(
                    fullname=user.full_name,
                    role=user.role,
                    db_session=db_session,
                    user=user,
                    is_update=True,
                ),
            )
            return

        await client.views_open(
            trigger_id=body["trigger_id"],
            view=await user_registration_form(
                db_session=db_session,
            ),
        )


def register_profile_shortcuts(app: AsyncApp):
    app.shortcut("profile")(handle_project_shorcut)
