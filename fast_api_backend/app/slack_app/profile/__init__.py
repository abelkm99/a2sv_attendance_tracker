from slack_bolt.async_app import AsyncApp
from app.slack_app.profile.actions import register_profile_actions
from app.slack_app.profile.events import register_profile_events

from app.slack_app.profile.shortcurs import register_profile_shortcuts


def register_profile_features(app: AsyncApp):
    register_profile_shortcuts(app=app)
    register_profile_actions(app=app)
    register_profile_events(app=app)
