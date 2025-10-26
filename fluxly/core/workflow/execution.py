from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, PrivateAttr, computed_field

from fluxly.core.status import StatusCodes
from fluxly.core.workflow.metadata import WorkflowMetadata
from fluxly.core.workflow.output import WorkflowOutput


class WorkflowExecution(BaseModel):
    metadata: Annotated[WorkflowMetadata, Field(description="Per-attempt workflow execution metadata")] = WorkflowMetadata()
    status: Annotated[StatusCodes, Field(description="Per-attempt workflow execution status")] = StatusCodes.WAITING
    output: Annotated[WorkflowOutput, Field(description="Per-attempt workflow output state")] = WorkflowOutput()

    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()))
    _attempt: int = PrivateAttr(default=1)

    @computed_field
    @property
    def attempt(self) -> int:
        return self._attempt

    @computed_field
    @property
    def id(self) -> str:
        return self._id

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)

    def __repr__(self) -> str:
        return self.__str__()
