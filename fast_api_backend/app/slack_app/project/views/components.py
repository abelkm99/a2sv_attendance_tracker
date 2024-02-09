from slack_sdk.models.blocks import (
    Block,
    InputBlock,
    Option,
    PlainTextObject,
    SectionBlock,
    StaticSelectElement,
    DividerBlock,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project


async def projects_option_component(
    unique_identifier: str,
    db_session: AsyncSession,
    initail_project: str | None = None,
) -> tuple[Block, bool]:
    projects: list[Project] = await Project.get_active_projects(db_session)

    if len(projects):
        if initail_project is None:
            return (
                InputBlock(
                    block_id=f"{unique_identifier}selected_project_block",
                    label=PlainTextObject(text="Project Name", emoji=True),
                    element=StaticSelectElement(
                        placeholder=PlainTextObject(
                            text="Select a project",
                            emoji=True,
                        ),
                        options=[
                            Option(text=project.name, value=project.name)
                            for project in projects
                        ],
                        action_id="static_select-action",
                    ),
                ),
                True,
            )
        else:
            return (
                InputBlock(
                    block_id=f"{unique_identifier}selected_project_block",
                    label=PlainTextObject(text="Project Name", emoji=True),
                    element=StaticSelectElement(
                        placeholder=PlainTextObject(
                            text="Select a project",
                            emoji=True,
                        ),
                        options=[
                            Option(text=project.name, value=project.name)
                            for project in projects
                        ],
                        action_id="static_select-action",
                        initial_option=Option(
                            text=initail_project,
                            value=initail_project,
                        ),
                    ),
                ),
                True,
            )

    return SectionBlock(text="No Project exists!!!"), False


DividerComponent = DividerBlock()
