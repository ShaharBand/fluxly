from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, PrivateAttr

from fluxcli.core.status import StatusCodes
from fluxcli.core.workflow.metadata import WorkflowMetadata
from fluxcli.core.workflow.output import WorkflowOutput


class WorkflowExecution(BaseModel):
    metadata: Annotated[WorkflowMetadata, Field(description="Per-attempt workflow execution metadata")] = WorkflowMetadata()
    status: Annotated[StatusCodes, Field(description="Per-attempt workflow execution status")] = StatusCodes.WAITING
    output: Annotated[WorkflowOutput, Field(description="Per-attempt workflow output state")] = WorkflowOutput()

    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()))

    @property
    def id(self) -> str:
        return self._id
