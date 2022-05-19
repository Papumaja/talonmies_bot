import datetime

def str_to_time(string: str):
    """Supports formats
    mm:ss
    hh:mm:ss
    dd:hh:mm:ss
    """
    try:
        parts = [int(p) for p in string.split(':')]
    except Exception:
        raise ValueError("Epähyvä aikamääre")

    n_parts = len(parts)
    if n_parts > 4 or n_parts < 2: raise ValueError("Epähyvä aikamääre")
    if n_parts == 2:
        return datetime.timedelta(minutes=parts[0], seconds=parts[1])
    elif n_parts == 3:
        return datetime.timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    elif n_parts == 4:
        return datetime.timedelta(days=parts[0], hours=parts[1], minutes=parts[2], seconds=parts[3])

