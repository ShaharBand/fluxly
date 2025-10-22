from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from flowcli.core.status import StatusCodes


class NodeError(BaseModel):
    status: Annotated[Enum, Field(description="Node error status")] = StatusCodes.FAILED
    exception_class_name: Annotated[str | None, Field(description="Exception class name")] = None
    exception_message: Annotated[str | None, Field(description="Error message")] = None

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)

    def __repr__(self):
        return self.__str__()
