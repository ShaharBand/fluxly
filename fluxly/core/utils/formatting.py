from datetime import datetime, timedelta


def format_datetime_to_humanreadable(dt: datetime | None) -> str | None:
    if not dt:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


def format_timedelta_to_humanreadable(td: timedelta | None) -> str | None:
    if not td:
        return None
    total_seconds = td.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s {milliseconds}ms"
