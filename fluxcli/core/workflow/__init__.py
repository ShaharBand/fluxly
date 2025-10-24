from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fluxcli.core.workflow.workflow import Workflow
    from fluxcli.core.workflow.graph import WorkflowGraph
    from fluxcli.core.workflow.input import WorkflowInput
    from fluxcli.core.workflow.metadata import WorkflowMetadata
    from fluxcli.core.workflow.output import WorkflowOutput
    from fluxcli.core.workflow.execution import WorkflowExecution
    from fluxcli.core.workflow.exceptions import NodesNotFoundException

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
        from fluxcli.core.workflow.workflow import Workflow
        return Workflow
    if name == "WorkflowGraph":
        from fluxcli.core.workflow.graph import WorkflowGraph
        return WorkflowGraph
    if name == "WorkflowInput":
        from fluxcli.core.workflow.input import WorkflowInput
        return WorkflowInput
    if name == "WorkflowOutput":
        from fluxcli.core.workflow.output import WorkflowOutput
        return WorkflowOutput
    if name == "WorkflowMetadata":
        from fluxcli.core.workflow.metadata import WorkflowMetadata
        return WorkflowMetadata
    if name == "WorkflowExecution":
        from fluxcli.core.workflow.execution import WorkflowExecution
        return WorkflowExecution
    if name == "NodesNotFoundException":
        from fluxcli.core.workflow.exceptions import NodesNotFoundException
        return NodesNotFoundException

    raise AttributeError(f"module 'fluxcli.core.workflow' has no attribute '{name}'")
