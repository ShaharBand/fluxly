from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field

from flowcli.core.node.execution import NodeExecution
from flowcli.core.status import StatusCodes


class WorkflowOutput(BaseModel):
    status: Annotated[Enum, Field(description="Workflow execution status")] = StatusCodes.WAITING
    nodes_executions: Annotated[list[NodeExecution], Field(description="Workflow nodes executions")] = []
