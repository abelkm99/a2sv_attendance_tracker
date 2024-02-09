from logging import Logger
from slack_bolt.async_app import AsyncAck
from app.database.database import get_db
from app.models.project import Project

from app.slack_app.project.views.delete_project import (
    delete_project_confirmation_view,
    project_deleted_succesfully_view,
)


async def handle_delete_project_first_step(
    ack: AsyncAck,
    body: dict,
):
    await ack()
    identifier: str = "project_delete_project_selected_project_block"

    # project name retrival
    project_name = body["view"]["state"]["values"]
    project_name = project_name[identifier]
    project_name = project_name["static_select-action"]
    project_name = project_name["selected_option"]["value"]
    await ack(
        response_action="update",
        view=delete_project_confirmation_view(project_name=project_name),
    )


async def handle_delete_project_confirmation_step(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
):
    # delete the project at this step and show project deleted succesfull page
    # with an ackowledgement of that the project has been deleted
    await ack()
    async with get_db() as db_session:
        project_name = body["view"]["private_metadata"]
        logger.debug(project_name)
        project = Project.get_project_by_name(
            db_session=db_session,
            name=project_name,
        )
        logger.info(project)
        if project:
            await Project.archive_project(
                db_session=db_session,
                name=project_name,
            )
        await ack(
            response_action="update",
            view=project_deleted_succesfully_view(project_name=project_name),
        )
