from datetime import datetime, timedelta
from pydantic import BaseModel, validator

from app.schemas.project_schema import ProjectBase


class TimeSheetBase(BaseModel):
    id: int
    check_in_time: datetime
    check_out_time: datetime
    elapsed_time: int
    location: str


class TimeSheetOut(TimeSheetBase):
    project: ProjectBase

    @validator("check_in_time", "check_out_time", pre=True, always=True)
    def add_three_hours(cls, v):
        # Ensure input is a datetime object before adding 3 hours
        if isinstance(v, datetime):
            return v + timedelta(hours=3)
        return v
