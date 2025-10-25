
from examples.structured_demo.nodes.alpha.execution import AlphaNodeExecution
from examples.structured_demo.workflow.input import DemoWorkflowInput
from fluxly.core.node.node import Node


class Alpha(Node):
    _workflow_input: DemoWorkflowInput

    @property
    def current_execution(self) -> AlphaNodeExecution:
        return super().current_execution

    @property
    def last_execution(self) -> AlphaNodeExecution:
        return super().last_execution

    @property
    def workflow_input(self) -> DemoWorkflowInput:
        return self._workflow_input

    def _create_execution(self) -> AlphaNodeExecution:
        return AlphaNodeExecution()

    def _logic(self) -> None:
        msg = self.workflow_input.message
        if not msg:
            msg = "hello from alpha"

        self.current_execution.output.echoed = msg
        self._logger.info(f"Alpha produced: {self.current_execution.output.echoed}")


