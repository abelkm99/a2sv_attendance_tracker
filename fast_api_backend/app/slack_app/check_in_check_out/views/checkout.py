from slack_sdk.models.views import View
from slack_sdk.models.blocks import (
    PlainTextObject,
    HeaderBlock,
    ContextBlock,
    DividerBlock,
    SectionBlock,
    MarkdownTextObject,
    Option,
    InputBlock,
    ImageElement,
    RadioButtonsElement,
)
from app.models.time_sheet import TimeSheet, get_elapsed_time
from app.models.user import User
from utils import convert_time_to_string, get_current_time

unique_identifier = "check-out_menu_"

current_datetime = get_current_time().strftime("%A, %b %d %Y, %I:%M%p")
current_date = get_current_time().strftime("%B %d, %Y")


def header(username):
    return HeaderBlock(
        block_id=f"{unique_identifier}header_block",
        text=PlainTextObject(text=f":tada: Welcome :back: {username} !!!", emoji=True),
    )


def subHeader(role, employement):
    return ContextBlock(
        block_id=f"{unique_identifier}SubHeader",
        elements=[
            MarkdownTextObject(text=f"*{current_date} * | *{employement}* - {role}")
        ],
    )


def information(elasped_time):
    return SectionBlock(
        text=f" *:clipboard: Total Elapsed Time is {elasped_time}:tada: *"
    )


def body(thumbnail, elasped_time, check_inTime):
    return SectionBlock(
        block_id=f"{unique_identifier}body",
        text=f"*Check-In Time* ;-  {check_inTime} \n *Dedicated Time* ;-  {elasped_time}",
        accessory=ImageElement(
            image_url=thumbnail,
            alt_text="user thumbnail",
        ),
    )


warning = ContextBlock(
    block_id=f"{unique_identifier}footer",
    elements=[
        ImageElement(
            image_url="https://api.slack.com/img/blocks/bkb_template_images/notificationsWarningIcon.png",
            alt_text="notifications warning icon",
        ),
        MarkdownTextObject(
            text="*you are expected to be at the office for 7 hours*",
        ),
    ],
)

productivity_form = InputBlock(
    label="Rate your Productiviy",
    element=RadioButtonsElement(
        action_id=f"{unique_identifier}productivity_form",
        options=[
            Option(text=" :star2::star2::star2::star2: ", value="3"),
            Option(text=" :star2::star2::star2: ", value="2"),
            Option(text=":sob:", value="1"),
        ],
    ),
)


def get_checkOut_form(user: User, last_check_in: TimeSheet):
    elasped_time = get_elapsed_time(last_checkin_time=last_check_in)
    thumbnail = user.profile_url
    name = user.full_name
    role = user.role
    employement = user.employement_status
    check_inTime = convert_time_to_string(last_check_in.check_in_time)

    return View(
        type="modal",
        callback_id=f"{unique_identifier}view_callback",
        title=PlainTextObject(text="Attendance Monitoring", emoji=True),
        close=PlainTextObject(text="Cancel", emoji=True),
        submit=PlainTextObject(text="Check-out :wave:", emoji=True),
        blocks=[
            header(name),
            subHeader(role, employement),
            DividerBlock(),
            information(elasped_time),
            body(thumbnail, elasped_time, check_inTime),
            warning,
            # DividerBlock(),
            # productivity_form
        ],
    )
