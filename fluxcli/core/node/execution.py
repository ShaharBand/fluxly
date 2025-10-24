from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, PrivateAttr

from fluxcli.core.node.error import NodeError
from fluxcli.core.node.metadata import NodeMetadata
from fluxcli.core.node.output import NodeOutput
from fluxcli.core.status import StatusCodes


class NodeExecution(BaseModel):
    metadata: Annotated[NodeMetadata, Field(description="Per-attempt execution metadata")] = NodeMetadata()
    status: Annotated[StatusCodes, Field(description="Node execution status")] = StatusCodes.WAITING
    output: Annotated[NodeOutput, Field(description="Per-attempt output state")] = NodeOutput()
    error: Annotated[NodeError | None, Field(description="Error for this attempt if failed")] = None

    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()))

    @property
    def id(self) -> str:
        return self._id
