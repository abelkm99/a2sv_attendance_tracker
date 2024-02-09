from logging import Logger
from slack_bolt.async_app import AsyncAck, AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from app.database.database import get_db
from app.models.daily_plan import DailyPlan, Task
from app.models.user import User
from app.slack_app.daily_plan.views.add_daily_plan import get_daily_plan_view
from app.slack_app.daily_plan.views.daily_plan_attachment import (
    build_daily_plan_attachement,
)
from app.slack_app.daily_plan.views.daily_plan_success import (
    daily_plan_published_succesfully,
    daily_plan_updated_succesfully,
)
from utils import get_current_time


def group_lines(message):
    lines = message.split("\n")
    groups = []
    current_group = ""
    for line in lines:
        if not line.startswith("-"):
            if current_group:
                groups.append(current_group)
            current_group = line
        else:
            current_group += "\n" + line
    if current_group:
        groups.append(current_group)
    return groups


async def handle_publish_daily_plan(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    try:
        async with get_db() as db_session:
            # get the tasks from the body
            data = body["view"]["blocks"]
            task_texts = [
                x["text"]["text"].replace("*", "")
                for x in data
                if "development-" in x["block_id"]
                or "problem_solving-" in x["block_id"]
            ]

            data = body["view"]["state"]["values"]

            keys = data.keys()
            tasks = []
            for key in keys:
                if "daily" not in key:
                    result = data[key]["daily_plan_ignore_action"]["selected_option"][
                        "value"
                    ]
                    key_splited = key.split("-")
                    tasks.append(
                        {
                            "task_type": key_splited[
                                0
                            ],  # development or problem solving
                            "task_id": key_splited[1],  # the task id on the database
                            "state": result,  # the current state done or not done
                        }
                    )
            # append the task detail to the tasks list
            for idx, task in enumerate(tasks):
                task["task"] = task_texts[idx]

            # get todays development tasks
            todays_tasks = []
            if data.get("daily_plan_development_task", None):
                todays_tasks = group_lines(
                    data["daily_plan_development_task"]["IGNORE"]["value"]
                )

            user = body["user"]
            task_completed = []
            task_not_completed = []

            completed_task_ids = set()

            for task in tasks:
                if task["task_type"] == "development":
                    if task["state"] == ":white_check_mark: Done":
                        task_completed.append(task["task"])
                        completed_task_ids.add(int(task["task_id"]))
                    else:
                        task_not_completed.append(task["task"])

            user = await User.get_user_by_slack_id(db_session, body["user"]["id"])

            if not user:
                await ack()
                return

            # check if i have published a daily PLAN on this day
            current_daily_plan = await DailyPlan.get_daily_plan_for_today(
                db_session=db_session,
                slack_id=user.slack_id,
            )
            # this will be the attachment that will be published
            prev_plan = await DailyPlan.update_prev_task_state(
                db_session=db_session,
                slack_id=user.slack_id,
                completed_task_ids=completed_task_ids,
            )

            attachment_tobe_published = build_daily_plan_attachement(
                dev_completed=task_completed,
                dev_not_completed=task_not_completed,
                todays_development=todays_tasks,
                user=user,
                prev_date=prev_plan.time_published if prev_plan else None,
                current_date=get_current_time(),
            )

            if current_daily_plan:
                # do update operations here if daily plan have already been posted
                response = await client.chat_update(
                    channel=current_daily_plan.channel_id,
                    ts=current_daily_plan.message_id,
                    attachments=attachment_tobe_published,
                )
                if response["ok"]:
                    current_daily_plan = await Task.update_daily_plan_tasks(
                        db_session=db_session,
                        daily_plan_id=current_daily_plan.id,
                        tasks=todays_tasks,
                    )
                    await ack(
                        response_action="update",
                        view=daily_plan_updated_succesfully(),
                    )
                return

            response = await client.chat_postMessage(
                channel=user.daily_plan_channel, attachments=attachment_tobe_published
            )

            if response["ok"]:
                # publish a new daily plan if it haven't
                await DailyPlan.create_daily_plan(
                    db_session=db_session,
                    user=user,
                    message_id=response["ts"],
                    tasks=todays_tasks,
                )
                await ack(
                    response_action="update",
                    view=daily_plan_published_succesfully(),
                )
                return
    except Exception as e:
        logger.error(e)


async def handle_daily_plan_from_attachment(
    ack: AsyncAck,
    client: AsyncWebClient,
    body: dict,
):
    async with get_db() as db_session:
        await ack()
        await client.views_open(
            trigger_id=body["trigger_id"],
            view=await get_daily_plan_view(body["user"]["id"], db_session),
        )
        return


def register_daily_plan_actions(app: AsyncApp):
    app.view("daily_plan_view_callback")(handle_publish_daily_plan)
    app.action("daily-plan-writer")(handle_daily_plan_from_attachment)
