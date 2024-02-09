import aiohttp
import ujson

from logging import Logger
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.fastapi.async_handler import AsyncSlackRequestHandler
from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_sdk.web.async_client import AsyncWebClient


from config import MySettings
from app.slack_app.check_in_check_out import register_checkIn_features
from app.slack_app.commands import register_commands
from app.slack_app.daily_plan import register_daily_plan_features
from app.slack_app.profile import register_profile_features
from app.slack_app.project import register_project_features

SlackAppInstance = AsyncApp(
    token=MySettings.SLACK_BOT_TOKEN,
    signing_secret=MySettings.SLACK_SIGNING_SECRET,
)

"""
TODO
    - prepare the system prompt
        mention that you are a slack assistant bot.
    - prepare the normal quesiton prompt
"""


async def make_request(text: str) -> tuple[str, int, int, int]:
    messages: list[dict[str, str]] = []

    messages.append({"role": "system", "content": MySettings.SYSTEM_PROMPT})
    messages.append(
        {"role": "user", "content": MySettings.QUESTION_PROMPT.format(text)}
    )

    url = "https://api.openai.com/v1/chat/completions"

    payload = ujson.dumps(
        {
            "model": "gpt-3.5-turbo-1106",
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 2048,
        }
    )

    headers = {
        "Authorization": f"Bearer {MySettings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data["choices"][0]["message"]["content"]
                    total_tokens = data["usage"]["total_tokens"]
                    prompt_tokens = data["usage"]["prompt_tokens"]
                    completion_tokens = data["usage"]["completion_tokens"]
                    return answer, prompt_tokens, completion_tokens, total_tokens
                else:
                    raise Exception(
                        f"Request failed with status code {response.status}\
                                error : {await response.text()}",
                    )
    except Exception as e:
        # Handle the exception here other exceptions here
        raise Exception(f"Request failed {str(e)}")


@SlackAppInstance.event("message")
async def handle_message_events(
    body: dict,
    logger: Logger,
    client: AsyncWebClient,
):
    logger.info(body)
    channel: str = body["event"]["channel"]
    user_id: str = body["event"]["user"]
    message = body["event"]["text"]
    ans, _, _, _ = await make_request(text=message)

    await client.chat_postEphemeral(channel=channel, user=user_id, text=ans)


# MIDDLEWARE EXAMPLE
# @slack_app_instance.use
# async def database_context_middleware(
#     client: AsyncWebClient,
#     context: AsyncBoltContext,
#     logger: Logger,
#     payload: dict,
#     next: Callable,
# ):
#     # add any kind of middleware operation here
#     await next()


# register the middleware
# slack_app.use(database_context_middleware)


# register the features here
register_project_features(app=SlackAppInstance)
register_profile_features(app=SlackAppInstance)
register_daily_plan_features(app=SlackAppInstance)
register_checkIn_features(app=SlackAppInstance)
register_commands(bot=SlackAppInstance)

SlackBotRequestHandler = AsyncSlackRequestHandler(SlackAppInstance)
SlackBotSocketModeHandler = AsyncSocketModeHandler(
    SlackAppInstance,
    MySettings.APP_TOKEN,
)
