from slack_sdk.models.blocks import (
    Block,
    ConversationFilter,
    ConversationSelectElement,
    HeaderBlock,
    InputBlock,
    MarkdownTextObject,
    PlainTextInputElement,
    PlainTextObject,
    SectionBlock,
    StaticSelectElement,
    Option,
)
from slack_sdk.models.views import View
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

from app.slack_app.project.views.components import projects_option_component


unique_identifier = "profile_register_"
header = HeaderBlock(text=PlainTextObject(text="Register", emoji=True))


def get_full_name_input(fullname: str | None):
    return InputBlock(
        label=PlainTextObject(text="Full Name", emoji=True),
        block_id=f"{unique_identifier}full_name_input_block",
        element=PlainTextInputElement(
            placeholder="Write Your Full Name",
            initial_value=fullname,
            action_id=f"{unique_identifier}full_name_input_action",
        )
        if fullname
        else PlainTextInputElement(
            placeholder="Write Your Full Name",
            action_id=f"{unique_identifier}full_name_input_action",
        ),
    )


def get_role_input(initial_value: str | None = None):
    return InputBlock(
        label=PlainTextObject(text="Title :briefcase:", emoji=True),
        block_id=f"{unique_identifier}role_input_block",
        element=(
            PlainTextInputElement(
                placeholder="Please Select Your Role at A2SV",
                action_id=f"{unique_identifier}role_input_action",
            )
            if initial_value is None
            else PlainTextInputElement(
                placeholder="Please Select Your Role at A2SV",
                action_id=f"{unique_identifier}role_input_action",
                initial_value=initial_value,
            )
        ),
    )


def get_employment_status(employement_status: str | None = None):
    pass

    return InputBlock(
        block_id=f"{unique_identifier}selected_employement_status_block",
        label=PlainTextObject(
            text="What is your Current Employment Status", emoji=True
        ),
        element=(
            StaticSelectElement(
                placeholder=PlainTextObject(text="Job Type", emoji=True),
                options=[
                    Option(text="Full-Time", value="Full-Time"),
                    Option(text="Part-Time", value="Part-Time"),
                    Option(text="Intern", value="Intern"),
                ],
                action_id=f"{unique_identifier}emoloyement_status_action",
            )
            if employement_status is None
            else StaticSelectElement(
                placeholder=PlainTextObject(text="Job Type", emoji=True),
                options=[
                    Option(text="Full-Time", value="Full-Time"),
                    Option(text="Part-Time", value="Part-Time"),
                    Option(text="Intern", value="Intern"),
                ],
                action_id=f"{unique_identifier}emoloyement_status_action",
                initial_option=Option(
                    text=employement_status, value=employement_status
                ),
            )
        ),
    )


def get_daily_plan_channel(daily_plan_channel: str | None = None):
    return InputBlock(
        element=(
            ConversationSelectElement(
                placeholder="Select a Channel",
                filter=ConversationFilter(
                    include=["public", "mpim"],
                ),
                action_id=f"{unique_identifier}daily_plan_channel_action",
            )
            if daily_plan_channel is None
            else ConversationSelectElement(
                placeholder="Select a Channel",
                filter=ConversationFilter(
                    include=["public", "mpim"],
                ),
                action_id=f"{unique_identifier}daily_plan_channel_action",
                initial_conversation=daily_plan_channel,
            )
        ),
        label="Choose the channel to publish your daily plan to:",
        block_id=f"{unique_identifier}daily_plan_channel_block",
    )


def get_headsup_channel(headsup_channel: str | None = None):
    return InputBlock(
        element=(
            ConversationSelectElement(
                placeholder="Select a Channel",
                filter=ConversationFilter(
                    include=["public", "mpim"],
                ),
                action_id=f"{unique_identifier}headsup_channel_action",
            )
            if headsup_channel is None
            else ConversationSelectElement(
                placeholder="Select a Channel",
                filter=ConversationFilter(
                    include=["public", "mpim"],
                ),
                action_id=f"{unique_identifier}headsup_channel_action",
                initial_conversation=headsup_channel,
            )
        ),
        label=(
            """Choose the channel to publish your"""
            """" Heads-Up :pleading_face: to:"""
        ),
        block_id=f"{unique_identifier}headsup_channel_block",
    )


def get_check_in_check_out_channel(check_in_check_out_channel: str | None = None):
    return InputBlock(
        element=(
            ConversationSelectElement(
                placeholder="Select a Channel",
                filter=ConversationFilter(
                    include=["public", "mpim"],
                ),
                action_id=f"{unique_identifier}check_in_check_out_channel_action",
            )
            if check_in_check_out_channel is None
            else ConversationSelectElement(
                placeholder="Select a Channel",
                filter=ConversationFilter(
                    include=["public", "mpim"],
                ),
                action_id=f"{unique_identifier}check_in_check_out_channel_action",
                initial_conversation=check_in_check_out_channel,
            )
        ),
        label="Choose the channel to notify people when you check in and check out",
        block_id=f"{unique_identifier}check_in_check_out_channel_block",
    )


def get_telegram_id_input(telegram_id: int | None = None):
    return InputBlock(
        label=PlainTextObject(text="Telegram ID", emoji=True),
        block_id=f"{unique_identifier}telegram_id_input_block",
        element=PlainTextInputElement(
            placeholder="Write Your Telegram ID",
            initial_value=str(telegram_id) if telegram_id else None,
            action_id=f"{unique_identifier}telegram_id_input_action",
        ),
        hint=PlainTextObject(
            text="Get your Telegram ID by sending /start on @A2SVBouncerbot on Telegram"
        ),
    )


async def user_registration_form(
    db_session: AsyncSession,
    fullname: str | None = None,
    role: str | None = None,
    user: User | None = None,
    is_update=False,
):
    # if project is archived don't then make project none
    project = (
        None if not user or not user.project or user.project.archived else user.project
    )

    # get the project input block component
    project_component, have_any = await projects_option_component(
        unique_identifier,
        db_session,
        project.name if project else None,
    )

    blocks: list[Block] = [
        header,
    ]

    if have_any:
        blocks.extend(
            [
                get_telegram_id_input(user.telegram_id if user else None),
                get_full_name_input(user.full_name if user else fullname),
                get_role_input(user.role if user else role),
                get_employment_status(user.employement_status if user else None),
                get_daily_plan_channel(user.daily_plan_channel if user else None),
                get_headsup_channel(user.headsup_channel if user else None),
                get_check_in_check_out_channel(
                    user.check_in_check_out_channel if user else None
                ),
                project_component,
            ]
        )

        return View(
            type="modal",
            callback_id=f"{unique_identifier}view_callback",
            title=PlainTextObject(text="Attendance Monitoring", emoji=True),
            submit=PlainTextObject(
                text=("Register" if not is_update else "Update"), emoji=True
            ),
            close=PlainTextObject(text="Cancel", emoji=True),
            blocks=blocks,
        )
    else:
        blocks.append(project_component)
        return View(
            type="modal",
            callback_id=f"{unique_identifier}view_callback",
            title=PlainTextObject(text="Attendance Monitoring", emoji=True),
            close=PlainTextObject(text="Cancel", emoji=True),
            blocks=blocks,
        )


def user_registered_succesfully_view(message):
    return View(
        type="modal",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        blocks=[
            HeaderBlock(
                text=PlainTextObject(text=":white_check_mark:Succesfull"),
            ),
            SectionBlock(text=MarkdownTextObject(text=message)),
        ],
    )
