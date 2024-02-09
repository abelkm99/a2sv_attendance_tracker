from logging import Logger
from slack_bolt.async_app import AsyncAck, AsyncApp
from slack_sdk.web.async_client import AsyncWebClient
from app.database.database import get_db
from app.slack_app.daily_plan.views.add_daily_plan import get_daily_plan_view


async def handle_daily_plan_shorcut(
    ack: AsyncAck,
    shortcut: dict,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    try:
        await ack()
        async with get_db() as db_session:
            # should i handle the business logic here
            # no it should be in it's own separate file called controller.py
            await ack()

            await client.views_open(
                trigger_id=body["trigger_id"],
                view=await get_daily_plan_view(
                    body["user"]["id"],
                    db_session,
                ),
            )
    except Exception as e:
        logger.error(e)


def register_daily_plan_shortcuts(app: AsyncApp):
    app.shortcut("daily_plan")(handle_daily_plan_shorcut)
    pass
