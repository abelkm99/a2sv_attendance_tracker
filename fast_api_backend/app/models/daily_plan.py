from datetime import datetime
from sqlalchemy import DateTime, Integer, String, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import mapped_column, Mapped, relationship, selectinload
from sqlalchemy.orm.properties import ForeignKey
from app.database import Base
from app.models.user import User
from utils import get_current_time


class Task(Base):
    __tablename__ = "task"
    id: Mapped[int] = mapped_column(primary_key=True)
    daily_plan_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("daily_plan.id"), nullable=False
    )
    task: Mapped[str] = mapped_column(String(5000), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    state: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    daily_plan: Mapped["DailyPlan"] = relationship(
        "DailyPlan",
        back_populates="tasks",
    )

    @classmethod
    async def delete_tasks(
        cls,
        db_session: AsyncSession,
        daily_plan_id: int,
    ):
        stmt = delete(cls).where(cls.daily_plan_id == daily_plan_id)
        await db_session.execute(stmt)
        await db_session.commit()

    @classmethod
    async def add_tasks(
        cls,
        db_session: AsyncSession,
        daily_plan_id: int,
        tasks: list[dict],
    ):
        for task in tasks:
            instance = cls(
                daily_plan_id=daily_plan_id, task=task, type="DEVELOPMENT", state=0
            )
            db_session.add(instance)
        await db_session.commit()

    @classmethod
    async def update_daily_plan_tasks(
        cls,
        db_session: AsyncSession,
        daily_plan_id: int,
        tasks: list[dict],
    ):
        await cls.delete_tasks(db_session, daily_plan_id)
        await cls.add_tasks(db_session, daily_plan_id, tasks)


class DailyPlan(Base):
    __tablename__ = "daily_plan"
    id: Mapped[int] = mapped_column(primary_key=True)
    slack_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("user.slack_id"), nullable=False
    )
    channel_id: Mapped[str] = mapped_column(String(50), nullable=False)
    time_published: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    message_id: Mapped[str] = mapped_column(String(50), nullable=False)

    tasks: Mapped[list["Task"]] = mapped_column()

    tasks: Mapped[list["Task"]] = relationship(
        "Task", back_populates="daily_plan", cascade="all,delete"
    )

    @classmethod
    async def create_daily_plan(
        cls,
        db_session: AsyncSession,
        user: User,
        message_id: str,
        tasks: list[dict],
    ):
        instance = cls(
            slack_id=user.slack_id,
            channel_id=user.daily_plan_channel,
            time_published=get_current_time(),
            message_id=message_id,
        )
        db_session.add(instance)
        await db_session.flush()
        temp_tasks: list[Task] = []
        for task in tasks:
            temp_tasks.append(
                Task(daily_plan_id=instance.id, task=task, type="DEVELOPMENT", state=0)
            )
        db_session.add_all(temp_tasks)
        await db_session.commit()
        return instance

    @classmethod
    async def get_previous_plan(
        cls,
        slack_id: str,
        db_session: AsyncSession,
    ):
        currrent_datetime = datetime.combine(get_current_time(), datetime.min.time())
        stmt = (
            select(cls)
            .options(selectinload(cls.tasks))
            .where(
                cls.slack_id == slack_id,
                cls.time_published < currrent_datetime,
            )
            .order_by(cls.time_published.desc())
            .limit(1)
        )

        result = await db_session.execute(stmt)
        instance: DailyPlan | None = result.scalar_one_or_none()
        return instance

    @classmethod
    async def get_daily_plan_for_today(
        cls,
        slack_id: str,
        db_session: AsyncSession,
    ):
        current_date = get_current_time().date()

        stmt = (
            select(cls)
            .options(selectinload(cls.tasks))
            .where(
                cls.slack_id == slack_id,
                func.date(cls.time_published) == current_date,
            )
            .order_by(cls.time_published.desc())
        )

        result = await db_session.execute(stmt)
        instance: DailyPlan | None = result.scalar_one_or_none()
        return instance

    @classmethod
    async def update_prev_task_state(
        cls,
        db_session: AsyncSession,
        slack_id: str,
        completed_task_ids: set,
    ):
        prev_daily_plan = await cls.get_previous_plan(slack_id, db_session)
        if prev_daily_plan:
            for task in prev_daily_plan.tasks:
                task.state = 1
                if task.id in completed_task_ids:
                    task.state = 1
                else:
                    task.state = 0
            await db_session.commit()
        return prev_daily_plan
