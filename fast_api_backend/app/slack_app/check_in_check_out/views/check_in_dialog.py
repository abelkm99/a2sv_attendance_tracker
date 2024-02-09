from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    HeaderBlock,
    ContextBlock,
    SectionBlock,
    ImageElement,
    PlainTextObject,
    MarkdownTextObject,
)

from app.models.user import User
from utils import convert_time_to_string, get_current_time

unique_identifier = "checkIn_Confirmation_"

header = HeaderBlock(text=" :tada: You Have Successfully Check-In")

# current_datetime = convert_time_to_string(get_current_time())


def subHeader(role, employement):
    return ContextBlock(
        block_id=f"{unique_identifier}SubHeader",
        elements=[
            MarkdownTextObject(
                text=f"*{get_current_time().strftime('%B %d, %Y')} * | *{employement}* - {role}"
            )
        ],
    )


def body(name, thumbnail):
    return SectionBlock(
        block_id=f"{unique_identifier}body",
        text=f" *{name}* \n *Check-In Time* ;- {convert_time_to_string(get_current_time())} \n",
        accessory=ImageElement(
            image_url=thumbnail,
            alt_text="user thumbnail",
        ),
    )


footer = ContextBlock(
    block_id=f"{unique_identifier}footer",
    elements=[
        ImageElement(
            image_url="https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
            alt_text="notifications warning icon",
        ),
        MarkdownTextObject(
            text="*Recommended Check-Out: 4:30pm*",
        ),
    ],
)


def get_confirmation_dialog(user: User):
    thumbnail = user.profile_url
    name = user.full_name
    role = user.role
    employement = user.employement_status
    return View(
        type="modal",
        callback_id=f"{unique_identifier}view_callback",
        title=PlainTextObject(text="Attendance Monitoring", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        blocks=[
            header,
            subHeader(role, employement),
            body(name, thumbnail),
        ],
    )
