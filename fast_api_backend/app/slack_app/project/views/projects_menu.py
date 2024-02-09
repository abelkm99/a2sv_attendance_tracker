from slack_sdk.models.blocks import (
    DividerBlock,
    HeaderBlock,
    SectionBlock,
    PlainTextObject,
    MarkdownTextObject,
    ButtonElement,
)

from slack_sdk.models.views import View

unique_identifier = "project_menu_"

header = HeaderBlock(
    text=PlainTextObject(text="Projects", emoji=True),
)

add_project_section = SectionBlock(
    text=MarkdownTextObject(text="Add a new Project"),
    accessory=ButtonElement(
        text=PlainTextObject(text="Add Project", emoji=True),
        action_id=f"{unique_identifier}add_new_project",
        style="primary",
    ),
)
update_project_section = SectionBlock(
    text=MarkdownTextObject(text="Edit the name of the project"),
    accessory=ButtonElement(
        text=PlainTextObject(text="Update Existing Project", emoji=True),
        action_id=f"{unique_identifier}update_project",
        style="primary",
    ),
)
delete_project_section = SectionBlock(
    text=MarkdownTextObject(text="Delete or Archive a Project"),
    accessory=ButtonElement(
        text=PlainTextObject(text="Delete Project", emoji=True),
        action_id=f"{unique_identifier}delete_project",
        style="danger",
    ),
)

divider = DividerBlock()


def get_project_menu():
    return View(
        type="modal",
        callback_id=f"{unique_identifier}view_callback",
        title=PlainTextObject(text="Attendance Monitoring", emoji=True),
        close=PlainTextObject(text="Cancel", emoji=True),
        blocks=[
            header,
            divider,
            add_project_section,
            divider,
            update_project_section,
            divider,
            delete_project_section,
        ],
    )
