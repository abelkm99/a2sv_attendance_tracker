from contextlib import asynccontextmanager
from aiogram.types import Update
from asyncpg.pool import asyncio
from fastapi import FastAPI, Request
import logging
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.telegram_bot import (
    BOT_COMMANDS,
    WEB_HOOK_PATH,
    WEB_HOOK_URL,
    run_pooling,
    bot,
    dp,
)
from config import EnvironmentOption, MySettings
from app.slack_app import SlackBotSocketModeHandler
from app import create_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    await bot.set_my_commands(BOT_COMMANDS)

    if MySettings.ENVIRONMENT == EnvironmentOption.DEVELOPMENT:
        logging.basicConfig(level=logging.DEBUG)
        await bot.delete_webhook()
        asyncio.create_task(run_pooling())
        await SlackBotSocketModeHandler.connect_async()

    elif MySettings.ENVIRONMENT == EnvironmentOption.PRODUCTION:
        res = await bot.get_webhook_info()
        if res.url != WEB_HOOK_PATH:
            await bot.set_webhook(WEB_HOOK_PATH)

    yield


app = create_app(MySettings, lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse("static/index.html")


@app.post(WEB_HOOK_URL, include_in_schema=False)
async def bot_webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    return await dp.feed_update(bot, update)
