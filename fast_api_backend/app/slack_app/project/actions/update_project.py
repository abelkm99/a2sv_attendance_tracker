from logging import Logger
from slack_bolt.async_app import AsyncAck

from app.database.database import get_db
from app.models.project import Project
from app.slack_app.project.views.update_project import (
    project_updated_succesfully_view,
)


def the_same_project_error_response():
    return {
        "response_action": "errors",
        "errors": {
            "project_update_project_input_block": "the previous\
                    project name and the new project name can't be the same"
        },
    }


def project_name_already_exists(new_project_name: str):
    return {
        "response_action": "errors",
        "errors": {
            "project_update_project_input_block": f"project with the \
                    name {new_project_name} already exists in the database"
        },
    }


async def handle_view_submission_update_project(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
):
    async with get_db() as db_session:
        logger.debug(body)
        prev_project_name = body["view"]["state"]["values"][
            "project_update_project_selected_project_block"
        ]["static_select-action"]["selected_option"]["value"]
        new_project_name = body["view"]["state"]["values"][
            "project_update_project_input_block"
        ]["project_update_project_new_project_name"]["value"]
        new_project_name = new_project_name.strip().capitalize()

        if prev_project_name == new_project_name:
            await ack(the_same_project_error_response())
            return

        project: Project | None = await Project.get_project_by_name(
            db_session=db_session,
            name=new_project_name,
        )
        if project:
            await ack(project_name_already_exists(new_project_name))
            return

        await Project.update_project(
            db_session=db_session,
            prev_name=prev_project_name,
            new_name=new_project_name,
        )
        await ack(
            response_action="update",
            view=project_updated_succesfully_view(
                prev_project_name,
                new_project_name,
            ),
        )
