from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    PlainTextObject,
    HeaderBlock,
    ContextBlock,
    DividerBlock,
    SectionBlock,
    StaticSelectElement,
    MarkdownTextObject,
    Option,
    InputBlock,
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.project import Project
from app.models.user import User
from utils import get_current_time


unique_identifier = "check-in_menu_"
current_date = get_current_time().strftime("%B %d, %Y")


def header(username):
    return HeaderBlock(
        block_id=f"{unique_identifier}header_block",
        text=PlainTextObject(text=f":tada: Welcome {username} !!!", emoji=True),
    )


def type_of_checkin(default_type):
    return HeaderBlock(
        block_id=f"{unique_identifier}check_type_block",
        text=PlainTextObject(text=default_type, emoji=True),
    )


def subHeader(role, employement):
    return ContextBlock(
        block_id=f"{unique_identifier}SubHeader",
        elements=[
            MarkdownTextObject(text=f"*{current_date} * | *{employement}* - {role}")
        ],
    )


title = SectionBlock(text=" :loud_sound: *Please fill your check-checkin* :blush:")


def select_working_location():
    return InputBlock(
        block_id=f"{unique_identifier}select_working_location",
        label="What is your preferred work location for the day?",
        element=StaticSelectElement(
            placeholder=PlainTextObject(
                text="select a preferable working location", emoji=True
            ),
            options=[
                Option(text=x, value=x)
                for x in [
                    "AAiT In Person",
                    "AASTU In Person",
                    "Abrehot In Person",
                    "ASTU In Person",
                    "Remote",
                ]
            ],
            action_id="selected_working_location-action",
        ),
    )


async def select_project(
    project_id: int,
    db_session: AsyncSession,
):
    projects: list[Project] = await Project.get_all_active_projects(
        db_session=db_session
    )
    project = list(filter(lambda project: project.id == project_id, projects))[0]
    return InputBlock(
        block_id=f"{unique_identifier}select_project",
        label=":clipboard: *Select the project*\n",
        hint="project you will be working on.",
        element=StaticSelectElement(
            placeholder=PlainTextObject(text="Select a project", emoji=True),
            options=[
                Option(text=project.name, value=project.name) for project in projects
            ],
            initial_option=Option(text=project.name, value=project.name),
            action_id="static_select-action",
        ),
    )


async def get_checkIn_form(
    db_session: AsyncSession,
    user: User,
):
    return View(
        type="modal",
        callback_id=f"{unique_identifier}view_callback",
        title=PlainTextObject(text="Attendance Monitoring", emoji=True),
        close=PlainTextObject(text="Cancel", emoji=True),
        submit=PlainTextObject(text="Check in :blush:", emoji=True),
        blocks=[
            header(user.full_name),
            DividerBlock(),
            subHeader(user.role, user.employement_status),
            DividerBlock(),
            title,
            await select_project(user.project_id, db_session),
            DividerBlock(),
            select_working_location()
            # lastCheckIn
        ],
    )
