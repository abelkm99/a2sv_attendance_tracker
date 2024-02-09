from slack_sdk.models.attachments import BlockAttachment
from app.models.user import User
from slack_sdk.models.blocks import (
    HeaderBlock,
    SectionBlock,
    PlainTextObject,
    MarkdownTextObject,
    ButtonElement,
    ImageElement,
    ActionsBlock,
)


header = HeaderBlock(text=PlainTextObject(text="-----🔔 Reminder 🔔-----", emoji=True))


def get_header_attachment():
    return BlockAttachment(blocks=[header])


def check_out_reminder_attachment(user: User):
    attachments = []
    # attachments.append(get_header_attachment())
    reminder_block = SectionBlock(
        text=f":wave: <@{user.slack_id}> This is your check out reminder!",
    )

    actions_block = ActionsBlock(
        elements=[
            ButtonElement(
                text="Check Out",
                style="danger",
                action_id="check_out_reminder_attachment_button",
            )
        ]
    )

    message_body = SectionBlock(
        text=PlainTextObject(
            text="Don't forget to check out and log your departure. It's time to end your day and record your attendance. Please click the 'Check Out' button to record your checkout.",
            emoji=True,
        ),
        accessory=ImageElement(
            image_url="https://en.pimg.jp/043/875/118/1/43875118.jpg",
            alt_text="user thumbnail",
        ),
    )
    attachments.append(
        BlockAttachment(
            blocks=[header, reminder_block, message_body, actions_block],
            color="#fd000e",
        )
    )

    return attachments


def already_checked_out_attachment():
    attachments = []

    attachments.append(
        BlockAttachment(
            blocks=[
                SectionBlock(
                    text=MarkdownTextObject(
                        text="You have already checked out. Thank you! 🙂🙂🙂"
                    )
                ),
            ],
            color="#fd000e",
        )
    )

    return attachments
