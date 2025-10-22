
from pydantic import BaseModel, PrivateAttr

from flowcli.core.cli.generator import build_click_group_with_commands
from flowcli.core.workflow.input import WorkflowInput
from flowcli.core.workflow.workflow import Workflow


class FlowCLI(BaseModel):
    # TODO: debug: bool = False
    # TODO: max_workers: int | None = None
    _commands: dict[str, tuple[Workflow, type[WorkflowInput]]] = PrivateAttr(default_factory=dict)

    def add_command(self, command_name: str, workflow: Workflow, workflow_input_cls: type[WorkflowInput]) -> None:
        if command_name in self._commands:
            raise ValueError(f"Command {command_name} already registered")
        if not isinstance(workflow, Workflow):
            raise TypeError("workflow must be a Workflow instance (pre-built with nodes and edges)")
        self._commands[command_name] = (workflow, workflow_input_cls)

    def run(self) -> None:
        # Prefer pure Click group to guarantee commands list visibility
        click_group = build_click_group_with_commands(self._commands)
        click_group()




