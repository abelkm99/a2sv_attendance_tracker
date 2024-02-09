from slack_sdk.models.blocks import (
    Block,
    HeaderBlock,
    InputBlock,
    PlainTextInputElement,
    SectionBlock,
    PlainTextObject,
    MarkdownTextObject,
)

from slack_sdk.models.views import View
from sqlalchemy.ext.asyncio import AsyncSession

from app.slack_app.project.views.components import (
    projects_option_component,
    DividerComponent,
)


unique_identifier = "project_update_project_"

header = HeaderBlock(text=PlainTextObject(text="Edit Project", emoji=True))
section = SectionBlock(text=MarkdownTextObject(text="*Edit Project Name*"))


def get_input_block():
    return InputBlock(
        element=PlainTextInputElement(
            placeholder="new project name",
            action_id=f"{unique_identifier}new_project_name",
        ),
        label=PlainTextObject(text="new project name", emoji=True),
        block_id=f"{unique_identifier}input_block",
    )


async def edit_project_view(db_session: AsyncSession):
    project_component, have_any = await projects_option_component(
        unique_identifier, db_session
    )
    blocks: list[Block] = [
        header,
        DividerComponent,
        project_component,
    ]
    if have_any:
        blocks.append(section)
        blocks.append(get_input_block())

        return View(
            type="modal",
            callback_id=f"{unique_identifier}edit_project_view",
            title=PlainTextObject(text="Attendance Tracker", emoji=True),
            submit=PlainTextObject(text="Update", emoji=True),
            blocks=blocks,
        )

    return View(
        type="modal",
        callback_id=f"{unique_identifier}edit_project_view",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        blocks=blocks,
    )


def project_updated_succesfully_view(
    prev_project_name: str,
    new_project_name: str,
):
    return View(
        type="modal",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        blocks=[
            HeaderBlock(text=PlainTextObject(text="✅Success")),
            DividerComponent,
            SectionBlock(
                text=MarkdownTextObject(
                    text=(
                        f"""Projet *{prev_project_name}* has been"""
                        f"""" updated to {new_project_name} successfully."""
                    )
                )
            ),
        ],
    )
