import logging
from datetime import datetime
from slack_sdk.models.blocks import (
    Block,
    DividerBlock,
    HeaderBlock,
    InputBlock,
    Option,
    PlainTextInputElement,
    PlainTextObject,
    ContextBlock,
    MarkdownTextObject,
    SectionBlock,
    StaticSelectElement,
)
from slack_sdk.models.views import View
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.daily_plan import DailyPlan, Task
from utils import get_current_time

unique_identifier = "daily_plan_"


header = HeaderBlock(text=PlainTextObject(text="Daily Plan 📋", emoji=True))
divider = DividerBlock()

daily_plans_header_sectionBlock = SectionBlock(
    text=MarkdownTextObject(text="*Reports*")
)


def get_today_header(current_date: str) -> ContextBlock:
    return ContextBlock(
        elements=[
            MarkdownTextObject(
                text=f"*📅* Toda's Daily Plan | *{current_date}*",
            )
        ]
    )


def get_previous_header(prev_datetime: str) -> ContextBlock:
    return ContextBlock(
        elements=[
            MarkdownTextObject(
                text=f"*📅* Previous Day Report | *{prev_datetime}*",
            )
        ]
    )


def get_tasks_input_block(todays_tasks: list[str]) -> InputBlock:
    return InputBlock(
        label=PlainTextObject(text="Tasks", emoji=True),
        element=PlainTextInputElement(
            multiline=True,
            initial_value="\n".join(todays_tasks),
            action_id="IGNORE",
        ),
        block_id=f"{unique_identifier}development_task",
    )


level_0 = "• "
level_1 = "» "
level_2 = "◦ "


def format_task(task):
    formatted_tasks = []
    lines = task.split("\n")

    for line in lines:
        if any(level in line for level in (level_0, level_1, level_2)):
            formatted_tasks.append(line)
            continue
        if line.startswith("--"):
            line = "\t\t" + level_2 + "_" + line[2:].strip() + "_"
        elif line.startswith("-"):
            line = "\t" + level_1 + "_" + line[1:].strip() + "_"
        else:
            line = level_0 + "_" + line.strip() + "_"
        formatted_tasks.append(line)
    final_text = "\n".join(formatted_tasks)
    return final_text


def generate_task_drop_down_option(tasks: list[Task], task_type: str):
    projects = [":white_check_mark: Done", ":x: Not Done"]
    return [
        SectionBlock(
            text=MarkdownTextObject(text=f"{format_task(task.task)}"),
            accessory=StaticSelectElement(
                placeholder=PlainTextObject(text="Select a project", emoji=True),
                options=[Option(text=project, value=project) for project in projects],
                action_id=f"{unique_identifier}ignore_action",
                initial_option=(
                    Option(text=projects[1], value=projects[1])
                    if task.state == 0
                    else Option(text=projects[0], value=projects[0])
                ),
            ),
            block_id=f"{task_type}-{task.id}",
        )
        for task in tasks
    ]


async def get_daily_plan_view(
    slack_id: str,
    db_session: AsyncSession,
):
    # get previous day tasks
    formater = "%B %d %Y"
    # get the previous day daily plan

    prev_daily_plan = await DailyPlan.get_previous_plan(
        slack_id=slack_id, db_session=db_session
    )


    current_daily_plan = await DailyPlan.get_daily_plan_for_today(
        slack_id=slack_id,
        db_session=db_session,
    )

    current_tasks: list[str] = []
    prev_tasks: list[str] = []

    if prev_daily_plan:
        for task in prev_daily_plan.tasks:
            prev_tasks.append(task.task)


    if current_daily_plan:
        for task in current_daily_plan.tasks:
            current_tasks.append(task.task)


    blocks: list[Block] = []

    blocks.extend(
        [
            divider,
            get_today_header(
                datetime.strftime(
                    get_current_time(),
                    formater,
                )
            ),
            get_tasks_input_block(
                todays_tasks=current_tasks,
            ),
        ]
    )

    # add the information block
    if prev_daily_plan:
        blocks.append(
            get_previous_header(
                datetime.strftime(
                    prev_daily_plan.time_published,
                    formater,
                )
            )
        )

    # daily plan header section
    blocks.extend(
        [
            divider,
            daily_plans_header_sectionBlock,
        ]
    )

    if prev_daily_plan and len(prev_tasks) > 0:
        blocks.extend(
            generate_task_drop_down_option(prev_daily_plan.tasks, "development")
        )

    return View(
        type="modal",
        callback_id=f"{unique_identifier}view_callback",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        submit=PlainTextObject(text="Publish", emoji=True),
        blocks=blocks,
    )
