from sqlalchemy import Boolean, String, false, select, true, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any


class Project(Base):
    __tablename__ = "project"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    archived: Mapped[bool] = mapped_column(
        Boolean, server_default=false(), nullable=False
    )

    users: Mapped[list["User"]] = relationship(
        "User", back_populates="project", cascade="all,delete"
    )
    timesheets: Mapped[list["TimeSheet"]] = relationship(
        "TimeSheet", back_populates="project"
    )

    @classmethod
    async def get_project_by_name(cls, db_session: AsyncSession, name: str):
        stmt = select(cls).where(cls.name == name)

        result = await db_session.execute(stmt)

        # return the first persona with the same id
        instance: Project | None = result.scalars().first()
        return instance

    @classmethod
    async def get_project_by_id(cls, db_session: AsyncSession, id: int):
        stmt = select(cls).where(cls.id == id)

        result = await db_session.execute(stmt)

        # return the first persona with the same id
        instance: Project | None = result.scalars().first()
        return instance

    @classmethod
    async def add_project(cls, db_session: AsyncSession, name: str):
        try:
            project = cls(name=name, archived=False)
            await project.save(db_session)
            return project
        except SQLAlchemyError as ex:
            raise ex

    @classmethod
    async def get_active_projects(cls, db_session: AsyncSession):
        stmt = select(cls).where(cls.archived == false())
        result = await db_session.execute(stmt)

        # return all personas created by the user
        instance: list[Project] = list(result.scalars().all())
        return instance

    @classmethod
    async def get_archived_projects(cls, db_session: AsyncSession):
        stmt = select(cls).where(cls.archived == true())

        result = await db_session.execute(stmt)

        # return all personas created by the user
        instance: list[Project] = list(result.scalars().all())
        return instance

    @classmethod
    async def get_all_projects(cls, db_session: AsyncSession):
        stmt = select(cls)

        result = await db_session.execute(stmt)

        # return all personas created by the user
        instance: list[Project] = list(result.scalars().all())
        return instance

    @classmethod
    async def get_all_active_projects(cls, db_session: AsyncSession):
        stmt = select(cls).where(cls.archived == false())
        result = await db_session.execute(stmt)
        # return all personas created by the user
        instance: list[Project] = list(result.scalars().all())
        return instance

    @classmethod
    async def archive_project(cls, db_session: AsyncSession, name: str):
        stmt = update(cls).where(cls.name == name).values({"archived": True})

        affected_rows = await db_session.execute(stmt)
        await db_session.commit()
        if affected_rows.rowcount == 0:
            raise Exception(f"project with the name {name} dosen't exist")

    @classmethod
    async def update_project(
        cls,
        db_session: AsyncSession,
        prev_name: str,
        new_name: str,
    ):
        stmt = (
            update(cls)
            .where(cls.name == prev_name)
            .values(
                {"name": new_name},
            )
        )

        affected_rows = await db_session.execute(stmt)
        await db_session.commit()
        if affected_rows.rowcount == 0:
            raise Exception(f"project with the name {new_name} dosen't exist")
        return True

    def __init__(self, **kw: Any):
        super().__init__(**kw)
