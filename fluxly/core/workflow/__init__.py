from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fluxly.core.workflow.exceptions import NodesNotFoundException
    from fluxly.core.workflow.execution import WorkflowExecution
    from fluxly.core.workflow.graph import WorkflowGraph
    from fluxly.core.workflow.input import WorkflowInput
    from fluxly.core.workflow.metadata import WorkflowMetadata
    from fluxly.core.workflow.output import WorkflowOutput
    from fluxly.core.workflow.workflow import Workflow

__all__ = [
    "Workflow",
    "WorkflowGraph",
    "WorkflowInput",
    "WorkflowOutput",
    "WorkflowMetadata",
    "WorkflowExecution",
    "NodesNotFoundException",
]


def __getattr__(name: str):
    if name == "Workflow":
        from fluxly.core.workflow.workflow import Workflow
        return Workflow
    if name == "WorkflowGraph":
        from fluxly.core.workflow.graph import WorkflowGraph
        return WorkflowGraph
    if name == "WorkflowInput":
        from fluxly.core.workflow.input import WorkflowInput
        return WorkflowInput
    if name == "WorkflowOutput":
        from fluxly.core.workflow.output import WorkflowOutput
        return WorkflowOutput
    if name == "WorkflowMetadata":
        from fluxly.core.workflow.metadata import WorkflowMetadata
        return WorkflowMetadata
    if name == "WorkflowExecution":
        from fluxly.core.workflow.execution import WorkflowExecution
        return WorkflowExecution
    if name == "NodesNotFoundException":
        from fluxly.core.workflow.exceptions import NodesNotFoundException
        return NodesNotFoundException

    raise AttributeError(f"module 'fluxly.core.workflow' has no attribute '{name}'")
