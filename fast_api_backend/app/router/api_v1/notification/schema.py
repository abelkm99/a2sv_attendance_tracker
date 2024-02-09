from pydantic import BaseModel


class SlackUser(BaseModel):
    slack_id: str
    telegram_id: int | None
    full_name: str
