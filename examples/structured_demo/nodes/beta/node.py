
from examples.structured_demo.nodes.beta.execution import BetaNodeExecution
from examples.structured_demo.workflow.input import DemoWorkflowInput
from fluxly.node import Node


class Beta(Node):
    _workflow_input: DemoWorkflowInput

    @property
    def current_execution(self) -> BetaNodeExecution:
        return super().current_execution

    @property
    def last_execution(self) -> BetaNodeExecution:
        return super().last_execution

    @property
    def workflow_input(self) -> DemoWorkflowInput:
        return self._workflow_input

    def _create_execution(self) -> BetaNodeExecution:
        return BetaNodeExecution()

    def _logic(self) -> None:
        suffix = self.workflow_input.suffix
        if not suffix:
            suffix = "!"

        self.current_execution.output.combined = f"processed{suffix}"
        self._logger.info(f"Beta produced: {self.current_execution.output.combined}")
