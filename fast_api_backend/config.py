from starlette.config import Config
from pydantic_settings import BaseSettings
from enum import Enum


class EnvironmentOption(Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


config = Config(".env")


class Settings(BaseSettings):
    APP_NAME: str = "Slack Bot Backend"
    APP_VERSION: str = "0.0.1"


class CryptSettings(BaseSettings):
    SECRET_KEY: str = config("SECRET_KEY", default="secret")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        default=60 * 24 * 7,
    )


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config(
        "ENVIRONMENT", default=EnvironmentOption.DEVELOPMENT
    )


class BaseConfig(EnvironmentSettings, Settings, CryptSettings):
    SLACK_BOT_TOKEN: str = config("SLACK_BOT_TOKEN", default="")
    SLACK_SIGNING_SECRET: str = config("SLACK_SIGNING_SECRET", default="")
    Telegram_BOT_TOKEN: str = config("Telegram_BOT_TOKEN", default="")
    APP_TOKEN: str = config("APP_TOKEN", default="")
    CORS_ORGINS: list[str] = ["*"]
    API_URL: str = config("API_URL", default="http://localhost:8000")
    OPENAI_API_KEY: str = config("OPENAI_API_URL", default="")
    SYSTEM_PROMPT: str = config(
        "SYSTEM_PROMPT",
        default="You are a help full assistant slack bot that helps people with grammar and panctuation",
    )
    QUESTION_PROMPT: str = config(
        "QUESTION_PROMPT",
        default="""
        Given a Slack message, I'd like you to identify any misspelled words or grammatical errors. If the message is grammatically correct and doesn't require any changes, simply respond with "Looks good to me."
        If there are improvements to be made, please respond with "Here are the improvements you can make," followed by specific suggestions in a formatted list. For example:
        ```
            Original Slack message:
            'Hey team, I'm very sick because of the cold that I caught yesterday and had a headache. For that reason I will not come to the office, but I have finished all my tasks for this sprint. Have a productive day.'

            Response:
            Here are the improvements you can make:
            - "I'm very sick because of the cold that I caught yesterday and had a headache."
              - Change to: ```I'm feeling very unwell due to the cold I caught yesterday and have a headache.```
            - "For that reason I will not come to the office, but I have finished all my tasks for this sprint."
              - Change to: ```As a result, I will not be coming to the office, but I have completed all my tasks for this sprint.```
            - "Have a Productive day"
              - Looks good to me.
        ```
        Please ensure that any revised messages after the changes are enclosed within three backticks so that users can easily copy and paste them. Additionally, include a brief comment explaining each change made from the original message.
        SlackMessage = ```{}```
        """,
    )

    def get_env(self):
        if self.ENVIRONMENT == EnvironmentOption.PRODUCTION:
            return ProdConfig()
        elif self.ENVIRONMENT == EnvironmentOption.TESTING:
            return TestConfig()
        else:
            return DevConfig()


class ProdConfig(BaseConfig):
    DATABASE_URL: str = config("PRODUCTION_DATABASE_URI", default="")


class DevConfig(BaseConfig):
    DATABASE_URL: str = config(
        "DEV_DATABASE_URI",
        default="",
    )


class TestConfig(BaseConfig):
    DATABASE_URL: str = config(
        "TEST_DATABASE_URI",
        default="postgresql+asyncpg://root:123456789@host.docker.internal:5457/slack-bot",
    )


MySettings = BaseConfig().get_env()

print("-" * 30)
print("starting", MySettings.ENVIRONMENT, "config")
print("-" * 30)
