from datetime import datetime
from typing import List
from slack_sdk.models.attachments import BlockAttachment, Attachment
from slack_sdk.models.blocks import (
    ContextBlock,
    DividerBlock,
    HeaderBlock,
    SectionBlock,
    PlainTextObject,
    MarkdownTextObject,
    ImageElement,
)

from app.models.user import User

DATE_FORMAT = "%B %d %Y"

unique_identifier = "daily_plan_"

header = HeaderBlock(
    text=PlainTextObject(text="-----:pencil2:  Daily Plan Report -----", emoji=True)
)
footer = HeaderBlock(
    text=PlainTextObject(
        text="---------------------------------------------------------------------",
        emoji=True,
    )
)

level_0 = "• "
level_1 = "» "
level_2 = "◦ "


def format_tasks(tasks):
    formatted_tasks = []
    for task in tasks:
        lines = task.split("\n")

        # pprint(lines)
        for line in lines:
            if any(level in line for level in (level_0, level_1, level_2)):
                formatted_tasks.append(line)
                continue
            if line.startswith("--") or line.startswith("—"):
                line = "\t\t" + level_2 + "_" + line[2:].strip() + "_"
            elif line.startswith("-"):
                line = "\t" + level_1 + "_" + line[1:].strip() + "_"
            else:
                line = level_0 + "_" + line.strip() + "_"
            formatted_tasks.append(line)
    final_text = "\n".join(formatted_tasks)
    return final_text


def get_header_attachment():
    return BlockAttachment(blocks=[header])


def get_footer_attahcment():
    return BlockAttachment(blocks=[footer])


def get_daily_plan_header_attachment(user: User):
    header_text_block = SectionBlock(
        text=MarkdownTextObject(text=" *-----* :pencil2:  *Daily Plan Report* *-----* ")
    )

    divider_block = DividerBlock()

    main_content_block = SectionBlock(
        text=MarkdownTextObject(
            text=f"*{user.full_name}*\n{user.role}\n {user.employement_status}"
        ),
        accessory=ImageElement(image_url=user.profile_url, alt_text="Profile Image"),
    )

    return BlockAttachment(
        blocks=[header_text_block, divider_block, main_content_block]
    )


def date_indicator_block(content: str, date: str):
    return BlockAttachment(
        blocks=[
            DividerBlock(),
            ContextBlock(
                elements=[
                    ImageElement(
                        image_url="https://www.worklifepsych.com/wp-content/uploads/2018/11/WLP_web_image-18-1000x801.png",
                        alt_text="random_image",
                    ),
                    MarkdownTextObject(
                        text=content + " " + f"*{date}*", verbatim=False
                    ),
                ]
            ),
            DividerBlock(),
        ]
    )


def build_daily_plan_attachement(
    dev_completed: List[str],
    dev_not_completed: List[str],
    todays_development: List[str],
    user: User,
    prev_date: datetime | None,
    current_date: datetime,
):
    attachments = []

    attachments.append(get_daily_plan_header_attachment(user))

    if any(
        [
            dev_completed,
            dev_not_completed,
        ]
    ):
        if prev_date:
            attachments.append(
                date_indicator_block(
                    content="Previous Day Report",
                    date=datetime.strftime(prev_date, DATE_FORMAT),
                )
            )
    if len(dev_completed):
        attachments.append(
            Attachment(
                color="good",
                title="Development Completed",
                text=format_tasks(dev_completed),
                markdown_in=["text"],
            )
        )
    if len(dev_not_completed):
        attachments.append(
            Attachment(
                color="#fd000e",
                title="Development Not Completed",
                text=format_tasks(dev_not_completed),
                markdown_in=["text"],
            )
        )

    attachments.append(
        date_indicator_block(
            content="Todays Plan ",
            date=datetime.strftime(current_date, DATE_FORMAT),
        )
    )

    if len(todays_development):
        attachments.append(
            Attachment(
                color="#1414ff",
                title="Todays Daily Plan",
                text=format_tasks(todays_development),
            )
        )

    return attachments
