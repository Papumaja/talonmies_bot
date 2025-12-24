import datetime
import functools
from telegram import Update
from telegram.ext import ContextTypes


def str_to_time(string: str):
    """Supports formats
    mm:ss
    hh:mm:ss
    dd:hh:mm:ss
    """
    try:
        parts = [int(p) for p in string.split(":")]
    except Exception:
        raise ValueError("Epähyvä aikamääre")

    n_parts = len(parts)
    if n_parts > 4 or n_parts < 2:
        raise ValueError("Epähyvä aikamääre")
    if n_parts == 2:
        return datetime.timedelta(minutes=parts[0], seconds=parts[1])
    elif n_parts == 3:
        return datetime.timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    elif n_parts == 4:
        return datetime.timedelta(
            days=parts[0], hours=parts[1], minutes=parts[2], seconds=parts[3]
        )


def allowed_users(allowed_users):
    def wrapped(fn):
        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            # Expects the update and context objects to be first arguments
            update: Update = args[0]
            if update.message.from_user.id in allowed_users:
                await fn(*args, **kwargs)
            else:
                print(
                    f"User {update.message.from_user.id} ({update.message.from_user.username}) not allowed to run command {update.message.text}"
                )

        return wrapper

    return wrapped
