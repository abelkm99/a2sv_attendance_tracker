from slack_sdk.models.blocks import (
    HeaderBlock,
    PlainTextObject,
)
from slack_sdk.models.views import View


def daily_plan_published_succesfully():
    return View(
        type="modal",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        blocks=[
            HeaderBlock(
                text=PlainTextObject(
                    text=":white_check_mark:Daily Plan Published Succesfully"
                )
            ),
        ],
    )


def daily_plan_updated_succesfully():
    return View(
        type="modal",
        title=PlainTextObject(text="Attendance Tracker", emoji=True),
        close=PlainTextObject(text="Close", emoji=True),
        blocks=[
            HeaderBlock(
                text=PlainTextObject(
                    text=":white_check_mark:Daily Plan Updated Succesfully"
                )
            ),
        ],
    )
