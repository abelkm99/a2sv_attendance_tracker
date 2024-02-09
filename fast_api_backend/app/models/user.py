from typing import Any
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from sqlalchemy import (
    BigInteger,
    Boolean,
    Integer,
    String,
    Time,
    delete,
    false,
    select,
    update,
)
from sqlalchemy.orm.properties import ForeignKey
from app.database.base import Base
from datetime import time


class User(Base):
    __tablename__ = "user"
    slack_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        unique=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(String(250), nullable=False)
    employement_status: Mapped[str] = mapped_column(String(50), nullable=False)
    daily_plan_channel: Mapped[str] = mapped_column(String(50), nullable=False)
    headsup_channel: Mapped[str] = mapped_column(String(50), nullable=False)
    check_in_check_out_channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        server_default=false(),
        nullable=False,
    )

    profile_url = mapped_column(String(1000), nullable=False)
    timezone: Mapped[str] = mapped_column(String(100), nullable=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("project.id"),
        index=True,
        nullable=False,
    )

    # FIXME: check if the telegram id is unique while registering and updating
    telegram_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        unique=True,
        index=True,
    )

    project: Mapped["Project"] = relationship("Project", back_populates="users")

    timesheets: Mapped[list["TimeSheet"]] = relationship(
        "TimeSheet", back_populates="user"
    )

    @classmethod
    async def create_new_user(
        cls,
        db_session: AsyncSession,
        slack_id: str,
        full_name: str,
        role: str,
        employement_status: str,
        daily_plan_channel: str,
        headsup_channel: str,
        check_in_check_out_channel: str,
        profile_url: str,
        project_id: int,
        telegram_id: int,
        timezone: str,
        is_admin=False,
    ):
        try:
            user = cls(
                slack_id=slack_id,
                full_name=full_name,
                role=role,
                employement_status=employement_status,
                daily_plan_channel=daily_plan_channel,
                headsup_channel=headsup_channel,
                check_in_check_out_channel=check_in_check_out_channel,
                profile_url=profile_url,
                project_id=project_id,
                telegram_id=telegram_id,
                timezone=timezone,
                is_admin=is_admin,
            )
            await user.save(db_session)
            return user
        except SQLAlchemyError as ex:
            raise ex

    @classmethod
    async def update_user(
        cls,
        db_session: AsyncSession,
        slack_id: str,
        **kwargs: dict[str, Any],
    ):
        try:
            stmt = update(cls).where(cls.slack_id == slack_id).values(**kwargs)
            affected_rows = await db_session.execute(stmt)
            await db_session.commit()
            if affected_rows.rowcount == 0:
                raise Exception(
                    f"User with the slack_id {slack_id} dosen't exist",
                )
        except SQLAlchemyError as ex:
            raise ex

    @classmethod
    async def get_user_by_slack_id(
        cls,
        db_session: AsyncSession,
        slack_id: str,
    ):
        stmt = (
            select(cls)
            .options(selectinload(cls.project))
            .where(cls.slack_id == slack_id)
        )
        result = await db_session.execute(stmt)
        instance: User | None = result.scalars().first()
        return instance

    @classmethod
    async def get_user_by_telegram_id(
        cls,
        db_session: AsyncSession,
        telegram_id: int,
    ):
        stmt = select(cls).where(cls.telegram_id == telegram_id)
        result = await db_session.execute(stmt)
        instance: User | None = result.scalars().first()
        return instance

    @classmethod
    async def get_user_with_project(
        cls,
        db_session: AsyncSession,
        slack_id: str,
    ):
        stmt = (
            select(cls)
            .options(selectinload(cls.project))
            .where(cls.slack_id == slack_id)
        )
        result = await db_session.execute(stmt)
        instance: User | None = result.scalars().first()
        return instance

    @classmethod
    async def get_all_users(
        cls,
        db_session: AsyncSession,
    ):
        stmt = select(cls)
        result = await db_session.execute(stmt)
        instance: list[User] = list(result.scalars().all())
        return instance


"""
create a table for storing users reminder time
columns = time(24 hour format time), slack_id from the user table
"""


class Reminder(Base):
    __tablename__ = "reminder"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        unique=True,
        index=True,
    )
    reminder_time: Mapped[Time] = mapped_column(Time, nullable=False)
    notification_type: Mapped[str] = mapped_column(String(100), nullable=False)
    slack_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("user.slack_id"),
        nullable=False,
    )

    # FIXME:  the checking function have to check that no other reminder within 1 hour range should exist
    # I couldn't decide weather adding this would be beneficial or not right now so i left it as it is.
    @classmethod
    async def create_new_reminder(
        cls,
        db_session: AsyncSession,
        reminder_time: time,
        notification_type: str,
        slack_id: str,
    ):
        stmt = select(cls).where(
            cls.reminder_time == reminder_time, cls.slack_id == slack_id
        )
        result = await db_session.execute(stmt)
        instance: Reminder | None = result.scalars().first()
        if instance:
            raise Exception("Reminder already exists for the given time and user")
        try:
            reminder = cls(
                reminder_time=reminder_time,
                notification_type=notification_type,
                slack_id=slack_id,
            )
            print("--" * 100)
            print(reminder.notification_type)
            db_session.add(reminder)
            await db_session.commit()
            return reminder
        except SQLAlchemyError as ex:
            raise ex

    @classmethod
    async def remove_reminder(
        cls,
        db_session: AsyncSession,
        slack_id: str,
        reminder_time: time,
    ):
        try:
            stmt = delete(Reminder).where(
                Reminder.slack_id == slack_id,
                Reminder.reminder_time == reminder_time,
            )
            affected_rows = await db_session.execute(stmt)
            await db_session.commit()
            if affected_rows.rowcount == 0:
                raise Exception(
                    f"Reminder with reminder_time {reminder_time} (24 hrs) dosen't exist for this user",
                )
        except SQLAlchemyError as ex:
            raise ex

    @classmethod
    async def get_all_reminders(
        cls,
        db_session: AsyncSession,
        slack_id: str,
    ):
        stmt = (
            select(cls)
            .where(cls.slack_id == slack_id)
            .order_by(cls.reminder_time.asc())
        )
        result = await db_session.execute(stmt)
        instance: list[Reminder] = list(result.scalars().all())
        return instance

    @classmethod
    async def clear_all_reminders(cls, db_session: AsyncSession, slack_id: str):
        stmt = delete(Reminder).where(Reminder.slack_id == slack_id)
        result = await db_session.execute(stmt)
        await db_session.commit()
        return result.rowcount
