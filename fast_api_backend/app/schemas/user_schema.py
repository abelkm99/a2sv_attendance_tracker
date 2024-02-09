from pydantic import BaseModel


class UserBase(BaseModel):
    slack_id: str
    full_name: str
    role: str
    employement_status: str
    daily_plan_channel: str
    headsup_channel: str
    check_in_check_out_channel: str
    is_admin: bool
    profile_url: str
    project_id: int
