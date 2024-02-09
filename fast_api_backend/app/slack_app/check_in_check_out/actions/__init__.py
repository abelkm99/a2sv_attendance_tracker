from slack_bolt.async_app import AsyncApp

from app.slack_app.check_in_check_out.actions.checkin import (
    handle_checkIn,
    handle_checkIn_action,
)
from app.slack_app.check_in_check_out.actions.checkout import (
    handle_checkOut,
    handle_checkOut_action,
)


def register_actions(app: AsyncApp):
    app.view("check-in_menu_view_callback")(handle_checkIn)
    app.view("check-out_menu_view_callback")(handle_checkOut)
    app.action("check_in_reminder_attachment_button")(handle_checkIn_action)
    app.action("check_out_reminder_attachment_button")(handle_checkOut_action)
