from fastapi import APIRouter, Request

from app.slack_app import SlackBotRequestHandler

slack_router = APIRouter(prefix="/slack")


@slack_router.post("/events")
async def slack_event(req: Request):
    return await SlackBotRequestHandler.handle(req)


@slack_router.post("/reminders")
async def slack_reminder(req: Request):
    return await SlackBotRequestHandler.handle(req)


@slack_router.post("/clear-reminders")
async def slack_clear_reminders(req: Request):
    return await SlackBotRequestHandler.handle(req)


@slack_router.post("/add-checkin-reminder")
async def slack_add_checkin_reminder(req: Request):
    return await SlackBotRequestHandler.handle(req)


@slack_router.post("/add-checkout-reminder")
async def slack_add_checkout_reminder(req: Request):
    return await SlackBotRequestHandler.handle(req)


@slack_router.post("/remove-reminder")
async def slack_remove_reminder(req: Request):
    return await SlackBotRequestHandler.handle(req)
