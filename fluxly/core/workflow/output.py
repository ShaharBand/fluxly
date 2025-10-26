from typing import Annotated

from pydantic import BaseModel, Field

from fluxly.core.node.execution import NodeExecution


class WorkflowOutput(BaseModel): 
    node_to_executions: Annotated[dict[str, list[NodeExecution]], Field(description="Mapping of node name to all its executions")] = {}

    def __str__(self) -> str:
        return self.model_dump_json(indent=2)

    def __repr__(self) -> str:
        return self.__str__()
