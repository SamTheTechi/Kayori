import pytz
from datetime import datetime


def get_current_time():
    return datetime.now(pytz.utc).astimezone(
        pytz.timezone("Asia/Kolkata")
    ).strftime('%Y-%m-%d %H:%M')
