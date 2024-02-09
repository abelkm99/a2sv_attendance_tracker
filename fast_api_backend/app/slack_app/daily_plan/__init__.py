from slack_bolt.async_app import AsyncApp
from app.slack_app.daily_plan.actions import register_daily_plan_actions

from app.slack_app.daily_plan.shortcuts import register_daily_plan_shortcuts


def register_daily_plan_features(app: AsyncApp):
    register_daily_plan_shortcuts(app=app)
    register_daily_plan_actions(app=app)
