from slack_bolt.async_app import AsyncApp
from app.slack_app.project.actions.add_project import (
    handle_add_new_project_charachter_change,
    handle_add_project_submission,
)
from app.slack_app.project.actions.delete_project import (
    handle_delete_project_confirmation_step,
    handle_delete_project_first_step,
)

from app.slack_app.project.actions.project_menu import (
    handle_open_delete_project_view,
    handle_open_new_project_view,
    handle_open_update_project_view,
)
from app.slack_app.project.actions.update_project import (
    handle_view_submission_update_project,
)


async def handle_some_action(ack, body, logger):
    await ack()
    logger.info(body)


def register_project_actions(app: AsyncApp):
    app.action("project_menu_add_new_project")(handle_open_new_project_view)
    app.action("project_menu_update_project")(handle_open_update_project_view)
    app.action("project_menu_delete_project")(handle_open_delete_project_view)

    # # handle project deletion first step
    app.view("project_delete_project_fist_step")(
        handle_delete_project_first_step,
    )

    app.view("project_delete_project_confirm_delete_project")(
        handle_delete_project_confirmation_step
    )

    # # add project features
    app.action("project_add_new_project_charachter_change_action")(
        handle_add_new_project_charachter_change
    )
    app.view("project_add_new_project_submission_callback")(
        handle_add_project_submission
    )

    # # update project feature
    app.view("project_update_project_edit_project_view")(
        handle_view_submission_update_project
    )
    pass
