from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import get_db_router

from app.models.time_sheet import TimeSheet
from app.models.user import User
from app.schemas.timesheet_schema import TimeSheetOut
from app.schemas.user_schema import UserBase


report_router = APIRouter(
    prefix="/report",
    tags=["Report"],
    responses={404: {"description": "Not found"}},
)


@report_router.get("/")
async def all_report():
    return {"report": "page"}


@report_router.get("/get_interval", response_model=list[TimeSheetOut])
async def get_interval(
    slack_id: str, db_session: AsyncSession = Depends(get_db_router)
):
    return await TimeSheet.get_users_checkin_checkout_history(
        db_session=db_session, slack_id=slack_id
    )


@report_router.get("/get_users", response_model=list[UserBase])
async def get_users(db_session: AsyncSession = Depends(get_db_router)):
    return await User.get_all_users(db_session=db_session)
