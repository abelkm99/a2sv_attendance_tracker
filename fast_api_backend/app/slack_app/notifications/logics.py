from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.time_sheet import (
    get_users_checkedin_since_morning,
    get_users_from_db_who_havent_checkedin,
    get_users_who_have_checkedin_today,
)
from app.models.user import User
from utils import get_current_time


GHANA_CHECKIN_CHANNEL_ID = "C05UAE05WBZ"


async def get_users_who_havent_checkedin(db_session: AsyncSession) -> list[User]:
    """
    Retrieve a list of users who haven't checked in on the current day.

    Returns:
    List[User]: A list of User objects representing users who haven't checked in today.

    Description:
    This function queries the database to fetch users who have not recorded any check-in time
    entries for the current day. It utilizes the `User` and `TimeSheet` models to identify users
    who lack any check-in records within the specified time frame (from the start of the current
    day to the end of the current day).

    Note:
    - Ensure the `User` and `TimeSheet` models are properly defined and related in the database.
    - TimeSheet records are checked against the current day's date using the `check_in_time`.
    - Adjust the timezone considerations if necessary for accurate date comparisons.
    - Returns an empty list if no users are found without check-in records for the current day.
    """
    return await get_users_from_db_who_havent_checkedin(
        db_session,
        GHANA_CHECKIN_CHANNEL_ID,
    )


async def get_users_who_havent_checkedout(db_session: AsyncSession) -> list[User]:
    # Get the current date and time
    current_time = datetime.utcnow()

    # Query to find users who have checked in but haven't checked out from morning till current time
    users_checked_in_not_out: list[User] = await get_users_checkedin_since_morning(
        db_session,
        GHANA_CHECKIN_CHANNEL_ID,
        current_time,
    )
    return users_checked_in_not_out


async def get_users_who_have_checked_in_and_checked_out(
    db_session: AsyncSession,
) -> list[User]:
    current_datetime = get_current_time()

    # Iterate over each user
    users: list[User] = await get_users_who_have_checkedin_today(
        db_session, current_datetime=current_datetime
    )
    return users
