from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient
from app.database.database import get_db
from app.models.project import Project
from app.slack_app.project.views.add_project import (
    add_project_error,
    add_project_normal,
    project_added_succesfully_view,
)


async def handle_add_new_project_charachter_change(
    body: dict,
    ack: AsyncAck,
    client: AsyncWebClient,
):
    async with get_db() as db_session:
        await ack()
        block_id = "project_add_new_project_block"
        action_name = "project_add_new_project_charachter_change_action"
        project_name = body["view"]["state"]
        project_name = project_name["values"][block_id][action_name]["value"]

        project = await Project.get_project_by_name(db_session, project_name)
        if project:
            await client.views_update(
                # Pass the view_id
                view_id=body["view"]["id"],
                hash=body["view"]["hash"],
                view=add_project_error(project_name),
            )
        await client.views_update(
            # Pass the view_id
            view_id=body["view"]["id"],
            hash=body["view"]["hash"],
            view=add_project_normal(),
        )


def error_response(project_name: str):
    return {
        "response_action": "errors",
        "errors": {
            "project_add_new_project_block": f"The project {project_name}\
                    already exists in\n the database.",
        },
    }


async def handle_add_project_submission(
    ack: AsyncAck,
    body: dict,
):
    async with get_db() as db_session:
        block_id = "project_add_new_project_block"
        action_name = "project_add_new_project_charachter_change_action"
        project_name = body["view"]["state"]["values"]
        project_name = project_name[block_id][action_name]["value"]
        project_name = project_name.strip().capitalize()
        project = await Project.get_project_by_name(
            db_session=db_session,
            name=project_name,
        )

        if project:
            await ack(error_response(project_name))
            return
        project = await Project.add_project(
            db_session=db_session,
            name=project_name,
        )

        await ack(
            response_action="update",
            view=project_added_succesfully_view(project_name=project_name),
        )
