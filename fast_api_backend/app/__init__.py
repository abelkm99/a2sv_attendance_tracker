from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.router.api_v1 import api_v1_router
from app.router.slack_webhook.route import slack_router
from config import BaseConfig


# from app.routers import api_v1_router
# from app.utils.logger import fast_api_logger


async def logger_middleware(request: Request, call_next):
    # request.state.logger = fast_api_logger
    response = await call_next(request)
    return response


def create_app(config: BaseConfig, lifespan) -> FastAPI:
    # fast_api_logger.info(f"App started as {config.CONFIG_TYPE}")
    app = FastAPI(title="Slack Bot", lifespan=lifespan)

    app.include_router(api_v1_router)
    app.include_router(slack_router)

    # app.include_router(api_v1_router)
    app.middleware("http")(logger_middleware)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.CORS_ORGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
