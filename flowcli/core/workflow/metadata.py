from typing import Annotated

from pydantic import BaseModel, Field, computed_field

from flowcli.core.utils.types import DatetimeReadable, TimedeltaReadable


class WorkflowMetadata(BaseModel):
    start_time: Annotated[DatetimeReadable, Field(description="Start datetime of the workflow execution.")] = None
    end_time: Annotated[DatetimeReadable, Field(description="End datetime of the workflow execution.")] = None
 
    @property
    def process_time(self) -> TimedeltaReadable:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)
