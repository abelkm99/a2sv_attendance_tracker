from slack_sdk.models.blocks import (
    Block,
    HeaderBlock,
    SectionBlock,
    PlainTextObject,
    MarkdownTextObject,
)
from sqlalchemy.ext.asyncio import AsyncSession


from slack_sdk.models.views import View

from app.slack_app.project.views.components import (
    DividerComponent,
    projects_option_component,
)


unique_identifier = "project_delete_project_"


# Define the header block
header = HeaderBlock(text=PlainTextObject(text="Delete Project", emoji=True))

confirm_delete_header = HeaderBlock(
    text=PlainTextObject(text="🛑🛑 Confirm Delete Project 🛑🛑", emoji=True)
)
# Define the section block
section = SectionBlock(
    text=MarkdownTextObject(
        text=(
            """*When a project is deleted, it will be marked as"""
            """inactive and moved """
            """to an archive, where it cannot be accessed or used in"""
            """the future*. *This Process is Irreversible*"""
        ),
        verbatim=True,
    )
)


def get_confirmation_sectionBlock(project_name):
    return SectionBlock(
        text=MarkdownTextObject(
            text=(
                """*Are you sure you want to delete the"""
                f"""" project \t👉 {project_name} 👈*\n *this"""
                """ process is IRREVERSIBLE*"""
            ),
        )
    )


# Define the input block with a static select element


async def delete_project_view(db_session: AsyncSession):
    project_component, have_any = await projects_option_component(
        unique_identifier, db_session
    )
    blocks: list[Block] = [
        header,
        section,
        DividerComponent,
        project_component,
    ]

    if have_any:
        return View(
            type="modal",
            callback_id=f"{unique_identifier}fist_step",
            title=PlainTextObject(text="Attendance Tracker", emoji=True),
            submit=PlainTextObject(text="Continue", emoji=True),
            blocks=blocks,
        )

    return View(
        type="modal",
        callback_id=f"{unique_identifier}fist_step",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        blocks=blocks,
    )


def delete_project_confirmation_view(project_name):
    return View(
        type="modal",
        callback_id=f"{unique_identifier}confirm_delete_project",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        submit=PlainTextObject(text="Continue", emoji=True),
        blocks=[
            confirm_delete_header,
            get_confirmation_sectionBlock(project_name=project_name),
        ],
        private_metadata=project_name,
    )


def project_deleted_succesfully_view(project_name):
    return View(
        type="modal",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        blocks=[
            HeaderBlock(text=PlainTextObject(text="✅Success")),
            DividerComponent,
            SectionBlock(
                text=MarkdownTextObject(
                    text=f"Projet *{project_name}* has been \
                            deleted Successfully"
                )
            ),
        ],
    )
