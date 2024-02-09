from datetime import datetime
import pytz


def convert_time_to_string(utc_time: datetime) -> str:
    utc_time = utc_time.replace(tzinfo=pytz.utc)
    addis_ababa_tz = pytz.timezone("Africa/Addis_Ababa")
    addis_ababa_time = utc_time.astimezone(addis_ababa_tz)
    str_time_zone = addis_ababa_time.strftime("%Y-%m-%d %H:%M:%S")
    return str_time_zone


def get_current_time():
    return datetime.utcnow().replace(microsecond=0)
