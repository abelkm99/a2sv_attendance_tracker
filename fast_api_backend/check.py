from enum import Enum
from app.database.database import get_db
from app.models import *
from sqlalchemy import text
from datetime import time, datetime
from faker import Faker

Faker.seed(1)
F = Faker()

temp = [F.random_int(0, 11) for _ in range(1000)]

session = None


def get_random_time():
    temp = str(F.random_int(0, 23)) + ":" + str(F.random_int(0, 11) * 5)
    temp = time(*map(int, temp.split(":")))
    return temp


get_random_time()


class NotificationType(str, Enum):
    CHECKIN = "checkin"
    CHECKOUT = "checkout"


def get_statement(
    notification_type: NotificationType,
):
    has_checkd_in: int = 0 if notification_type == NotificationType.CHECKIN else 1
    current_time = datetime.utcnow().strftime("%H:%M")
    current_time = "21:40"
    print(current_time)

    stmt = f"""
select
	slack_id,
	telegram_id,
	checked_in,
    full_name
from
  (
    select
      users.slack_id,
      users.full_name,
      users.telegram_id,
      sum(
        case when ts.check_in_time >= CAST(
          DATE_TRUNC('day', current_date) AS TIMESTAMP
        )
        AND ts.check_out_time IS null then 1 else 0 end
      ) as checked_in
    from
      (
        select
          slack_id,
          full_name,
          telegram_id
        FROM
          (
            select
              u.full_name,
              u.telegram_id,
              r.slack_id,
              r.notification_type,
              r.id as reminder_id,
              current_date + r.reminder_time as normal_time,
              u.timezone,
              (
                (current_date + r.reminder_time) AT TIME ZONE u.timezone
              ) AT TIME ZONE 'UTC' AS start_time,
              (
                (current_date + r.reminder_time) AT TIME ZONE u.timezone + INTERVAL '1 hour'
              ) AT TIME ZONE 'UTC' AS end_time
            FROM
              public.reminder AS r
              JOIN public."user" u ON u.slack_id = r.slack_id
            where r.notification_type = '{notification_type.value}'
          ) AS calculated_times
        where
          start_time <= start_time::date + '{current_time}'::time
          and end_time::date +  '{current_time}'::time < end_time
        group by
          slack_id,
          full_name,
          telegram_id
        order by
          full_name
      ) as users
      join time_sheet ts on ts.slack_id = users.slack_id
    group by
      users.slack_id,
      users.full_name,
      users.telegram_id
  ) as result
where checked_in = {has_checkd_in}
    """
    return stmt


async def get_session():
    async with get_db() as session:
        stmt = text(get_statement(NotificationType.CHECKIN))
        # print(stmt)
        res = await session.execute(stmt)
        print("normal_time \t\t start_time \t\t end_time\t")
        for i in res:
            print(i)

        pass
        # users = await User.get_all_users(session)
        # reminders = []
        # for i in range(200):
        #     random_user = F.random_element(users)
        #     r = Reminder(reminder_time=get_random_time(), notification_type="checkin", slack_id=random_user.slack_id)
        #     reminders.append(r)
        # session.add_all(reminders)
        # await session.commit()


import asyncio

asyncio.run(get_session())
