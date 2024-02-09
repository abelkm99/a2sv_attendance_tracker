from slack_bolt.async_app import AsyncApp
from app.slack_app.check_in_check_out.actions import register_actions

from app.slack_app.check_in_check_out.shortcuts import register_shortcuts


def register_checkIn_features(app: AsyncApp):
    register_shortcuts(app=app)
    register_actions(app=app)
