from logging import Logger
from app.database.database import get_db
from app.models.user import User


async def handle_profile_change(
    body: dict,
    logger: Logger,
):
    try:
        async with get_db() as db_session:
            new_image_url = body["event"]["user"]["profile"]["image_512"]
            timezone = body["event"]["user"]["tz"]
            await User.update_user(
                db_session,
                body["event"]["user"]["id"],
                profile_url=new_image_url,
                timezone=timezone,
            )
    except Exception as ex:
        logger.error(ex)


def register_profile_events(app):
    app.event("user_change")(handle_profile_change)
