from slack_sdk.models.attachments import Attachment, BlockAttachment
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


def attachmet_create(
    slack_id: str,
    header_message: str,
    body_message: str,
    attachment_color: str,
    action_id: str,
    image_url: str,
    button_option: bool,
    button_name: str,
    button_color: str,
) -> list[Attachment]:
    attachments = []
    # attachments.append(get_header_attachment())
    reminder_block = SectionBlock(
        text=f"Hey :wave: <@{slack_id}> {header_message} :slightly_smiling_face:",
    )

    actions_block = ActionsBlock(
        elements=[
            ButtonElement(text=button_name, style=button_color, action_id=action_id)
        ]
    )

    message_body = SectionBlock(
        text=PlainTextObject(text=body_message, emoji=True),
        accessory=ImageElement(
            # image_url="https://cdn.xxl.thumbs.canstockphoto.com/check-in-stamp-sign-text-word-logo-green-clip-art_csp42781525.jpg",
            image_url=image_url,
            alt_text="user thumbnail",
        ),
    )
    blocks = [
        header,
        reminder_block,
        message_body,
    ]
    if button_option:
        blocks.append(actions_block)
    attachments.append(BlockAttachment(blocks=blocks, color=attachment_color))

    return attachments


def already_checked_in_attachment():
    attachments = []

    attachments.append(
        BlockAttachment(
            blocks=[
                SectionBlock(
                    text=MarkdownTextObject(
                        text="You have already checked in. Thank you! 🙂🙂🙂"
                    )
                ),
            ],
            color="#fd000e",
        )
    )
    # attachments.append(BlockAttachment(
    #     color="#f2c744",

    # )
    # )
    return attachments
