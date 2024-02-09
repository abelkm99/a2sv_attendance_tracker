import time
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    BotCommand,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)
from aiogram.utils.markdown import hbold
from app.models.user import User
from app.slack_app import SlackAppInstance

from config import MySettings
from app.database.database import get_db
from app.models.time_sheet import TimeSheet, get_elapsed_time
from utils import convert_time_to_string, get_current_time

WEB_HOOK_URL = f"/bot/{MySettings.Telegram_BOT_TOKEN}"
WEB_HOOK_PATH = f"{MySettings.API_URL}{WEB_HOOK_URL}"
bot = Bot(token=MySettings.Telegram_BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

BOT_COMMANDS: list[BotCommand] = [
    BotCommand(command="start", description="Open Menu"),
    BotCommand(command="checkin", description="Open Menu"),
    BotCommand(command="checkout", description="Open Menu"),
]

"""
TODO:
    [ ] preparing the text's emojis and everything and decorate the text that are being sent 
        - fix all the grammatical mistakes if there are any
    [x] merging the checkin with checkouts
        - cancled
    [x] adding elapsed time
        - add the elspead time to the checkout messae and also callback to cancel or confirm
    [x] add expire time for the callbacks
        - old callbacks shouln't work (if they took longer time than 1 mins delete that callback)
    [x] n * 2 rows for the location buttons.
    [ ] prepareing the function for the push notification
        - it should take a telegram_id
        it will use bo.send_message(telegram_id, text)
    [x] slash-command webhook support for the slack app reminders.
    [x] fix the checkout reminder slack message
    [x] fix the telegram_bot webhook
    [x] force people to enter their telegram_id when they try to checkin on the slack 

    [ ] add the cron job
        - prepare the cron expression
"""

locations = [
    "AAiT In Person",
    "AASTU In Person",
    "ASTU In Person",
    "Remote",
    "Abrehot In Person",
]

location_callback_mapper = {
    "AAiT In Person": "location:AAiT",
    "AASTU In Person": "location:AASTU",
    "ASTU In Person": "location:ASTU",
    "Remote": "location:Remote",
    "Abrehot In Person": "location:Abrehot",
}


async def send_checkin_reminder_message(telegram_id: int, name: str) -> None:
    message = f""" {hbold("🔔 Checkin Reminder 🔔 ")}
{hbold(f"Hey 👋 {name}")}

{hbold("This is your check in reminder")}.

It's time to start your day and log your attendance.
Please select the location to record your arival
    """

    temp_keyboard: list[list[InlineKeyboardButton]] = []
    row = 2
    for i in range(0, len(locations), row):
        temp_keyboard.append(
            [
                InlineKeyboardButton(
                    text=locations[j],
                    callback_data=location_callback_mapper[locations[j]],
                )
                for j in range(i, min(i + row, len(locations)))
            ]
        )
    await bot.send_message(
        telegram_id,
        message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=temp_keyboard,
            row_width=2,
        ),
    )
    pass


async def send_checkout_reminder_message(telegram_id: int, name: str) -> None:
    message = f""" {hbold("🔔 Checkout Reminder 🔔 ")}
{hbold(f"Hey 👋 {name}")}

{hbold("This is your checkout reminder")}.

Don't forget to check out and log your departure.
Please click the 'Check-Out' button to record your checkout.
    """
    await bot.send_message(
        telegram_id,
        message,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Check out",
                        callback_data="checkout_callback",
                    )
                ]
            ],
        ),
    )


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(
        f"Hi there 👋,\nThis is your Telegram ID\n\n👉 `{message.from_user.id}` 👈\n\nMake sure to add it to your slack profile by sendin /profile command",
        parse_mode="MARKDOWN",
    )


@dp.message(Command("checkin"))
async def cmd_check_in(message: Message) -> None:
    temp_keyboard: list[list[InlineKeyboardButton]] = []
    row = 2
    for i in range(0, len(locations), row):
        temp_keyboard.append(
            [
                InlineKeyboardButton(
                    text=locations[j],
                    callback_data=location_callback_mapper[locations[j]],
                )
                for j in range(i, min(i + row, len(locations)))
            ]
        )

    await message.reply(
        "Choose the location you want to check-in to",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=temp_keyboard,
            row_width=2,
        ),
    )


async def send_user_checked_in_message(db_user: User):
    await SlackAppInstance.client.chat_postMessage(
        channel=db_user.check_in_check_out_channel,
        text=f"<@{db_user.slack_id}> has checked out at {convert_time_to_string(get_current_time())}",
    )


async def send_user_checked_in_messa(db_user: User, location: str):
    await SlackAppInstance.client.chat_postMessage(
        channel=db_user.check_in_check_out_channel,
        text=f"<@{db_user.slack_id}> has checked-in {'Remotely' if location == 'Remote' else 'In-Person'}{(' at ' + location.split(' ')[0]) if location != 'Remote' else ''} at {convert_time_to_string(get_current_time())}",
    )


@dp.message(Command("checkout"))
async def cmd_check_out(message: Message) -> None:
    # add the following function for the checkout
    async with get_db() as db_session:
        try:
            if not message.from_user:
                raise Exception("User not found")

            last_check_in: TimeSheet | None = (
                await TimeSheet.get_checkin_stats_telegram(
                    db_session, telegram_id=message.from_user.id
                )
            )

            if not last_check_in:
                await message.reply("You haven't checked in yet")
                return

            elasped_time = get_elapsed_time(last_checkin_time=last_check_in)

            await message.reply(
                f"You have checked in at {convert_time_to_string(last_check_in.check_in_time)}\n\nElapsed time: {elasped_time}",
                reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text="Check out",
                                callback_data="checkout_callback",
                            )
                        ]
                    ],
                ),
            )
            return
        except Exception as e:
            await message.answer(f"Error: {e}")

    return


@dp.callback_query(lambda c: c.data == "checkout_callback")
async def process_checkout_callback(callback_query: CallbackQuery) -> None:
    if not callback_query.data:
        raise Exception("Invalid Callback Query")

    if not callback_query.message:
        raise Exception("Invalid Callback Query")

    initial_time, current_time = int(callback_query.message.date.timestamp()), int(
        time.time()
    )
    diff = abs(initial_time - current_time)
    diff /= 60
    if diff > 60 * 24:  # 1 day
        await callback_query.message.delete()
        await bot.send_message(
            callback_query.from_user.id,
            "Sorry, the callback has expired please try again",
        )
        return
    async with get_db() as db_session:
        try:
            res = await TimeSheet.telegram_checkout(
                db_session, callback_query.from_user.id
            )
            await bot.delete_message(
                callback_query.from_user.id, callback_query.message.message_id
            )
            if res["success"]:
                # delete the previous message
                db_user: User = res["user"]
                await send_user_checked_in_message(db_user)
                await bot.send_message(
                    callback_query.from_user.id,
                    "Checked out successfully",
                )
            else:
                await bot.send_message(
                    callback_query.from_user.id,
                    f"{res['message']}",
                )
        except Exception:
            await bot.delete_message(
                callback_query.from_user.id, callback_query.message.message_id
            )
            await bot.send_message(
                callback_query.from_user.id,
                "This telegram id is not registered on the slack bot",
            )


@dp.callback_query(lambda c: c.data.startswith("location"))
async def process_callback(callback_query: CallbackQuery) -> None:
    if not callback_query.data:
        raise Exception("Invalid Callback Query")

    if not callback_query.message:
        raise Exception("Invalid Callback Query")

    initial_time, current_time = int(callback_query.message.date.timestamp()), int(
        time.time()
    )
    diff = abs(initial_time - current_time)
    diff /= 60
    if diff > 60 * 24:  # 1 day
        await callback_query.message.delete()
        await bot.send_message(
            callback_query.from_user.id,
            "Sorry, the callback has expired please try again",
        )
        return

    arr = callback_query.data.split(":")
    print(arr)
    if arr[0] == "location":
        async with get_db() as db_session:
            try:
                res = await TimeSheet.telegram_checkin(
                    db_session, callback_query.from_user.id, arr[1]
                )
                await bot.delete_message(
                    callback_query.from_user.id, callback_query.message.message_id
                )
                if res["success"]:
                    # delete the previous message
                    db_user: User = res["user"]
                    await send_user_checked_in_messa(db_user, arr[1])
                    await bot.send_message(
                        callback_query.from_user.id,
                        f"Checked in at {arr[1]} successfully",
                    )
                else:
                    await bot.send_message(
                        callback_query.from_user.id,
                        f"{res['message']}",
                    )

            except Exception:
                await bot.delete_message(
                    callback_query.from_user.id, callback_query.message.message_id
                )

                await bot.send_message(
                    callback_query.from_user.id,
                    "This telegram id is not registered on the slack bot",
                )


async def run_pooling() -> None:
    await dp.start_polling(bot, handle_signals=False)
