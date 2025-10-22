from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flowcli.core.workflow.workflow import Workflow
    from flowcli.core.workflow.graph import WorkflowGraph
    from flowcli.core.workflow.input import WorkflowInput
    from flowcli.core.workflow.metadata import WorkflowMetadata
    from flowcli.core.workflow.output import WorkflowOutput
    from flowcli.core.workflow.execution import WorkflowExecution
    from flowcli.core.workflow.exceptions import NodesNotFoundException

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
        from flowcli.core.workflow.workflow import Workflow
        return Workflow
    if name == "WorkflowGraph":
        from flowcli.core.workflow.graph import WorkflowGraph
        return WorkflowGraph
    if name == "WorkflowInput":
        from flowcli.core.workflow.input import WorkflowInput
        return WorkflowInput
    if name == "WorkflowOutput":
        from flowcli.core.workflow.output import WorkflowOutput
        return WorkflowOutput
    if name == "WorkflowMetadata":
        from flowcli.core.workflow.metadata import WorkflowMetadata
        return WorkflowMetadata
    if name == "WorkflowExecution":
        from flowcli.core.workflow.execution import WorkflowExecution
        return WorkflowExecution
    if name == "NodesNotFoundException":
        from flowcli.core.workflow.exceptions import NodesNotFoundException
        return NodesNotFoundException

    raise AttributeError(f"module 'flowcli.core.workflow' has no attribute '{name}'")
