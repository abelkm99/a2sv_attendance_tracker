from fastapi import APIRouter
from app.router.api_v1.report.route import report_router
from app.router.api_v1.notification.route import notification_router

api_v1_router = APIRouter(prefix="/api_v1")


api_v1_router.include_router(notification_router)
api_v1_router.include_router(report_router)
