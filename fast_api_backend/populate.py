# import asyncio
# from slack_sdk.web.async_client import AsyncWebClient
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.database.database import get_db

# from app.models.user import User
# from config import settings


# async def get_data(db_session: AsyncSession):
#     stmt = select(User)
#     result = await db_session.execute(stmt)
#     instance: list[User] = list(result.scalars().all())

#     return instance


# async def main():
#     async with get_db() as db_session:
#         res = await get_data(db_session)
#         client = AsyncWebClient(token=settings.SLACK_BOT_TOKEN)

#         ans = await client.users_info(user=res[0].slack_id)
#         print(ans)

#     pass


# if __name__ == "__main__":
#     asyncio.run(main())
