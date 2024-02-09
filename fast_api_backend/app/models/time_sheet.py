from datetime import datetime, timedelta
from typing import Any
import pytz

from sqlalchemy import DateTime, Integer, String, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.properties import ForeignKey
from app.database.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload

from app.models.project import Project
from app.models.user import User
from utils import get_current_time


class TimeSheet(Base):
    __tablename__ = "time_sheet"
    id: Mapped[int] = mapped_column(primary_key=True)
    check_in_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    check_out_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    slack_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("user.slack_id"), nullable=False
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id"),
        index=True,
        nullable=False,
    )
    elapsed_time: Mapped[int] = mapped_column(Integer, nullable=True)
    location: Mapped[str] = mapped_column(
        String(100), nullable=True, server_default=text("In Person")
    )

    project: Mapped["Project"] = relationship("Project", back_populates="timesheets")
    user: Mapped["User"] = relationship("User", back_populates="timesheets")

    @classmethod
    async def get_users_checkin_checkout_history(
        cls,
        db_session: AsyncSession,
        slack_id: str,
    ):
        """
        get all the users checkin checkout history
        """
        stmt = (
            select(cls)
            .where(
                cls.slack_id == slack_id,
                cls.check_out_time.isnot(None),
            )
            .options(selectinload(cls.project))
            .order_by(cls.check_out_time.desc())
        )
        result = await db_session.execute(stmt)
        instances: list[TimeSheet] = list(result.scalars().all())
        return instances

    @classmethod
    async def get_checkin_stats(cls, db_session: AsyncSession, slack_id: str):
        """
        get checkin stats for a user by slack_id on the current day
        if the user have check that have null check_out_time on the current day then return that row
        """

        user = await User.get_user_by_slack_id(db_session, slack_id)

        if not user:
            raise ValueError(f"Invalid slack_id: {slack_id}")

        # today according to the users timezone
        current_time = (
            get_current_time()
            .astimezone(pytz.timezone(user.timezone))
            .replace(tzinfo=None)
        )
        start_of_day = datetime.combine(current_time, datetime.min.time())

        # FIXME: i have to take users current timezone into consideration
        stmt = (
            select(cls)
            .join(User, User.slack_id == cls.slack_id)
            .where(
                cls.slack_id == slack_id,
                cls.check_in_time >= start_of_day,
                cls.check_in_time <= current_time,
                cls.check_out_time.is_(None),
            )
        )

        result = await db_session.execute(stmt)
        instance: TimeSheet | None = result.scalars().first()
        return instance

    @classmethod
    async def get_checkin_stats_telegram(
        cls, db_session: AsyncSession, telegram_id: int
    ):
        """
        get checkin stats for a user by slack_id on the current day
        if the user have check that have null check_out_time on the current day then return that row
        """

        user = await User.get_user_by_telegram_id(db_session, telegram_id)

        if not user:
            raise ValueError(f"Invalid telegram_id: {telegram_id}")

        # today according to the users timezone
        current_time = (
            get_current_time()
            .astimezone(pytz.timezone(user.timezone))
            .replace(tzinfo=None)
        )
        start_of_day = datetime.combine(current_time, datetime.min.time())

        # FIXME: i have to take users current timezone into consideration
        stmt = (
            select(cls)
            .join(User, User.slack_id == cls.slack_id)
            .where(
                User.telegram_id == telegram_id,
                cls.check_in_time >= start_of_day,
                cls.check_in_time <= current_time,
                cls.check_out_time.is_(None),
            )
        )

        result = await db_session.execute(stmt)
        instance: TimeSheet | None = result.scalars().first()
        return instance

    @classmethod
    async def telegram_checkin(
        cls,
        db_session: AsyncSession,
        telegram_id: int,
        location: str,
    ):
        db_user: User | None = await User.get_user_by_telegram_id(
            db_session, telegram_id
        )
        if not db_user:
            raise Exception(f"User with the telegram_id {telegram_id} dosen't exist")

        time_sheet: TimeSheet | None = await cls.get_checkin_stats(
            db_session, db_user.slack_id
        )

        if time_sheet:
            return {
                "success": False,
                "message": "Already checked in!",
            }

        new_time_sheet: TimeSheet = cls(
            check_in_time=get_current_time(),
            slack_id=db_user.slack_id,
            project_id=db_user.project_id,
            location=location,
        )
        await new_time_sheet.save(db_session=db_session)
        return {
            "success": True,
            "message": "success fully checked in",
            "user": db_user,
        }

    @classmethod
    async def checkin_operation(
        cls,
        db_session: AsyncSession,
        slack_id: str,
        projec_name: str,
        location: str,
    ) -> dict[Any, Any]:
        project: Project | None = await Project.get_project_by_name(
            db_session=db_session, name=projec_name
        )
        if not project:
            return {
                "success": False,
                "message": f"project with the name {projec_name} doesn't exit.",
            }
        time_sheet: TimeSheet | None = await cls.get_checkin_stats(db_session, slack_id)

        if time_sheet:
            check_in_time_str = time_sheet.check_in_time.strftime("%Y-%m-%d %H:%M:%S")
            return {
                "success": False,
                "message": f"user has already been checked int at {check_in_time_str}",
            }

        # if the is no checkin row for the user then create one

        new_time_sheet: TimeSheet = cls(
            check_in_time=get_current_time(),
            slack_id=slack_id,
            project_id=project.id,
            location=location,
        )
        await new_time_sheet.save(db_session=db_session)
        return {"success": True, "message": "success fully checked in"}

    @classmethod
    async def checkout_operation(
        cls,
        db_session: AsyncSession,
        slack_id: str,
    ):
        time_sheet: TimeSheet | None = await cls.get_checkin_stats(db_session, slack_id)
        if not time_sheet:
            return {"success": False, "message": "user hasn't checked in yet."}

        check_out_time = get_current_time()
        time_sheet.check_out_time = check_out_time
        time_sheet.elapsed_time = int(
            (time_sheet.check_out_time - time_sheet.check_in_time).total_seconds()
        )

        db_session.add(time_sheet)
        await db_session.commit()
        return {
            "success": True,
            "message": "success fully checked out",
        }

    @classmethod
    async def telegram_checkout(
        cls,
        db_session: AsyncSession,
        telegram_id: int,
    ):
        db_user: User | None = await User.get_user_by_telegram_id(
            db_session, telegram_id
        )
        if not db_user:
            raise Exception(f"User with the telegram_id {telegram_id} dosen't exist")

        time_sheet: TimeSheet | None = await cls.get_checkin_stats(
            db_session, db_user.slack_id
        )
        if not time_sheet:
            return {"success": False, "message": "user hasn't checked in yet."}

        check_out_time = get_current_time()
        time_sheet.check_out_time = check_out_time
        time_sheet.elapsed_time = int(
            (time_sheet.check_out_time - time_sheet.check_in_time).total_seconds()
        )

        db_session.add(time_sheet)
        await db_session.commit()
        return {
            "success": True,
            "message": "success fully checked out",
            "user": db_user,
        }


def convert_second(seconds) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60

    time_str = ""
    if hours > 0:
        time_str += f"{hours} hour{'s' if hours > 1 else ''}"

    if minutes > 0:
        if time_str:
            time_str += ", "
        time_str += f"{minutes} minute{'s' if minutes > 1 else ''}"

    # if seconds > 0:
    #     if time_str:
    #         time_str += ", "
    #     time_str += f"{seconds} second{'s' if seconds > 1 else ''}"

    return time_str


def get_elapsed_time(last_checkin_time: TimeSheet):
    """Returns the elapsed time since the last check-in of a user.

    Args:
        last_checkin_time (Timesheet): Last Checkin Time Object

    Returns:
        str: The elapsed time in HH:MM:SS format.
        print(convert_seconds(12319)) -> 03:25:19
    Raises:
        ValueError: If slack_id is invalid or not found.

    """
    current_time = get_current_time()
    diff = current_time - last_checkin_time.check_in_time
    return convert_second(diff.total_seconds())


async def get_users_from_db_who_havent_checkedin(
    db_session: AsyncSession,
    ghana_checkin_channel: str,
) -> list[User]:
    current_datetime = get_current_time()
    start_of_today = datetime.combine(current_datetime.date(), datetime.min.time())
    """
    select * from "user" u where u.slack_id not in (select slack_id from time_sheet ts where ts.check_out_time is null);
    """

    subquery = select(TimeSheet.slack_id).where(
        TimeSheet.check_out_time.is_(None),
        TimeSheet.check_in_time >= start_of_today,
        TimeSheet.check_in_time <= current_datetime,
    )

    # Get all users who haven't checked in today if there is one check in checkout history it will filter it out
    stmt = (
        select(User)
        .where(
            User.slack_id.notin_(subquery),
            User.check_in_check_out_channel != ghana_checkin_channel,
        )
        .distinct()
    )
    print(stmt)
    result = await db_session.execute(stmt)
    users: list[User] = list(result.scalars().all())

    return users


async def get_users_checkedin_since_morning(
    db_session: AsyncSession,
    ghana_checkin_channel: str,
    current_time: datetime,
):
    today = current_time.today()
    start_of_today = datetime.combine(today, datetime.min.time())
    stmt = (
        select(User)
        .join(TimeSheet)
        .filter(
            (TimeSheet.check_in_time >= start_of_today)
            & (TimeSheet.check_in_time <= current_time)
            & (TimeSheet.check_out_time.is_(None))  # Checking for NULL check_out_time
        )
        .filter(User.check_in_check_out_channel != ghana_checkin_channel)
        .distinct()
    )
    result = await db_session.execute(stmt)
    users: list[User] = list(result.scalars().all())
    return users


async def get_users_who_have_checkedin_today(
    db_session: AsyncSession,
    current_datetime: datetime,
):
    current_date = datetime.combine(current_datetime.date(), datetime.min.time())

    """
    get all users who have checked in and checked out today
    and also that doesn't have checkout time that is none
    """

    stmt = (
        select(User)
        .join(TimeSheet, User.slack_id == TimeSheet.slack_id)
        .filter(
            (TimeSheet.check_in_time >= current_date)
            & (TimeSheet.check_in_time < current_date + timedelta(days=1))
        )
        .filter(TimeSheet.check_out_time.isnot(None))
        .distinct()
    )
    result = await db_session.execute(stmt)
    users: list[User] = list(result.scalars().all())
    return users
