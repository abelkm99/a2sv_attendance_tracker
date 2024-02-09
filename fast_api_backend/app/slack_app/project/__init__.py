from slack_bolt.async_app import AsyncApp
from app.slack_app.project.actions import register_project_actions
from app.slack_app.project.shortcuts import register_project_shortcuts


def register_project_features(app: AsyncApp):
    register_project_shortcuts(app=app)
    register_project_actions(app=app)
