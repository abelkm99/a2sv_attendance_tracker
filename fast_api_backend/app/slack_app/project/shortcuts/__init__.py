from logging import Logger
from slack_bolt.async_app import AsyncAck, AsyncApp
from slack_sdk.web.async_client import AsyncWebClient
from app.slack_app.project.views.projects_menu import get_project_menu


async def handle_project_shorcut(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    await ack()
    logger.info(body)
    await client.views_open(
        trigger_id=body["trigger_id"],
        view=get_project_menu(),
    )


def register_project_shortcuts(app: AsyncApp):
    app.shortcut("projects")(handle_project_shorcut)
