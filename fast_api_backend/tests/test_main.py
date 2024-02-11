from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project


@pytest.mark.asyncio
async def test_add_project(db_session: AsyncSession):
    test_project = Project(name="test")
    db_session.add(test_project)
    await db_session.commit()
    await db_session.reset()


@pytest.mark.asyncio
async def test_get_project(db_session: AsyncSession):
    project = await Project.get_project_by_name(db_session, name="test")
    assert project is not None
    assert project.name == "test"


def test_sample():
    assert 1 == 1


@pytest.mark.asyncio
async def test_check_route(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
