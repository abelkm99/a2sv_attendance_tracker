from slack_bolt.async_app import AsyncApp

from app.slack_app.profile.actions.register_user import (
    handel_user_registration_submission,
)


def register_profile_actions(app: AsyncApp):
    app.view("profile_register_view_callback")(handel_user_registration_submission)
    # app.action("profile_menu_register_user")(handel_user_registration)
