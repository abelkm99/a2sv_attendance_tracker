from logging import Logger
from slack_bolt.async_app import AsyncAck
from slack_sdk.web.async_client import AsyncWebClient

from app.database.database import get_db
from app.models.project import Project
from app.models.user import User
from app.slack_app.profile.views.register import (
    user_registered_succesfully_view,
)
from typing import Any


async def handel_user_registration_submission(
    ack: AsyncAck,
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    async with get_db() as db_session:
        view_state = body["view"]["state"]["values"]
        try:
            response = await client.users_info(user=body["user"]["id"])

            profile_picture = response["user"]["profile"]["image_512"]
            timezone = response["user"]["tz"]
            slack_id = body["user"]["id"]

            full_name = view_state["profile_register_full_name_input_block"][
                "profile_register_full_name_input_action"
            ]["value"]

            role = view_state["profile_register_role_input_block"][
                "profile_register_role_input_action"
            ]["value"]
            employment_status = view_state[
                "profile_register_selected_employement_status_block"
            ]["profile_register_emoloyement_status_action"]["selected_option"]["value"]

            daily_plan_channel = view_state[
                "profile_register_daily_plan_channel_block"
            ]["profile_register_daily_plan_channel_action"]["selected_conversation"]
            headsup_channel = view_state["profile_register_headsup_channel_block"][
                "profile_register_headsup_channel_action"
            ]["selected_conversation"]

            check_in_check_out_channel = view_state[
                "profile_register_check_in_check_out_channel_block"
            ]["profile_register_check_in_check_out_channel_action"][
                "selected_conversation"
            ]
            project_name = view_state["profile_register_selected_project_block"][
                "static_select-action"
            ]["selected_option"]["value"]

            telegram_id = view_state["profile_register_telegram_id_input_block"][
                "profile_register_telegram_id_input_action"
            ]["value"]
            # check if telegram_id can be converted to int
            try:
                telegram_id = int(telegram_id)
            except Exception:
                await ack(
                    {
                        "response_action": "errors",
                        "errors": {
                            "profile_register_telegram_id_input_block": "telegram id should only be a number."
                        },
                    }
                )
                return

            user: User | None = await User.get_user_by_slack_id(
                db_session=db_session, slack_id=slack_id
            )
            project: Project | None = await Project.get_project_by_name(
                db_session=db_session, name=project_name
            )

            if not project:
                raise Exception(f"Project with the name {project_name} dosen't exist")

            if user:
                data: dict[str, Any] = {
                    "full_name": full_name,
                    "role": role,
                    "employement_status": employment_status,
                    "daily_plan_channel": daily_plan_channel,
                    "headsup_channel": headsup_channel,
                    "check_in_check_out_channel": check_in_check_out_channel,
                    "profile_url": profile_picture,
                    "project_id": project.id,
                    "timezone": timezone,
                    "telegram_id": telegram_id,
                }
                await User.update_user(db_session=db_session, slack_id=slack_id, **data)

                await ack(
                    response_action="update",
                    view=user_registered_succesfully_view(
                        message="*Profile has been updated Successfully*"
                    ),
                )
                return

            await User.create_new_user(
                db_session=db_session,
                slack_id=slack_id,
                full_name=full_name,
                role=role,
                employement_status=employment_status,
                daily_plan_channel=daily_plan_channel,
                headsup_channel=headsup_channel,
                profile_url=profile_picture,
                check_in_check_out_channel=check_in_check_out_channel,
                project_id=project.id,
                telegram_id=telegram_id,
                timezone=timezone,
            )
            await ack(
                response_action="update",
                view=user_registered_succesfully_view(
                    message=f"New Member *{full_name}* Added Successfully"
                ),
            )

        except Exception as e:
            logger.error(e)
