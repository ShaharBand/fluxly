from datetime import datetime, timedelta
from typing import Annotated

from pydantic import PlainSerializer

from fluxly.core.utils.formatting import (
    format_datetime_to_humanreadable,
    format_timedelta_to_humanreadable,
)

DatetimeReadable = Annotated[
    datetime | None,
    PlainSerializer(lambda v: format_datetime_to_humanreadable(v)),
]

TimedeltaReadable = Annotated[
    timedelta | None,
    PlainSerializer(lambda v: format_timedelta_to_humanreadable(v)),
]
