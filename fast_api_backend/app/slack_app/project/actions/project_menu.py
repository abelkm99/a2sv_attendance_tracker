from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from logging import Logger
from app.database.database import get_db

from app.slack_app.project.views.add_project import add_project_normal
from app.slack_app.project.views.delete_project import delete_project_view
from app.slack_app.project.views.update_project import edit_project_view


async def handle_open_new_project_view(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    await ack()
    logger.info(body)
    await client.views_push(
        view_id=body["view"]["id"],
        # String that represents view state to protect against race conditions
        hash=body["view"]["hash"],
        trigger_id=body["trigger_id"],
        view=add_project_normal(),
    )


async def handle_open_update_project_view(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    async with get_db() as db_session:
        await ack()
        logger.info(body)
        await client.views_push(
            view_id=body["view"]["id"],
            hash=body["view"]["hash"],
            trigger_id=body["trigger_id"],
            view=await edit_project_view(db_session=db_session),
        )


async def handle_open_delete_project_view(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    async with get_db() as db_session:
        await ack()
        logger.info(body)
        await client.views_push(
            view_id=body["view"]["id"],
            hash=body["view"]["hash"],
            trigger_id=body["trigger_id"],
            view=await delete_project_view(db_session=db_session),
        )
