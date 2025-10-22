import threading
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, PrivateAttr

from flowcli.core.exceptions import TimeoutException, WorkflowException
from flowcli.core.node.error import NodeError
from flowcli.core.node.execution import NodeExecution
from flowcli.core.status import StatusCodes
from flowcli.core.workflow.input import WorkflowInput
from flowcli.core.workflow.metadata import WorkflowMetadata
from flowcli.services import LoggerConfig, LoggerService


class Node(ABC, BaseModel):
    name: Annotated[str, Field(..., max_length=30, min_length=3, description="The name of the node.")]
    description: Annotated[str, Field(max_length=128, min_length=3, description="The description of the node.")] | None = None
    timeout_seconds: Annotated[int, Field(gt=0, description="Timeout for the node in seconds.")] | None = None
    max_retries: Annotated[int, Field(ge=0, description="Maximum number of run attempts allowed in case of failure.")] = 0
    retry_delay_seconds: Annotated[int, Field(ge=0, description="Delay between retries in seconds.")] = 0

    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()))
    _executions: list[NodeExecution] = PrivateAttr(default_factory=list)
    _workflow_input: WorkflowInput | None = PrivateAttr(default=None)
    _workflow_metadata: WorkflowMetadata | None = PrivateAttr(default=None)
    _logger: LoggerService = LoggerService(config=LoggerConfig())

    @property
    def id(self) -> str:
        return self._id

    @property
    def executions(self) -> tuple[NodeExecution, ...]:
        return tuple(self._executions)

    @property
    def workflow_input(self) -> WorkflowInput | None:
        return self._workflow_input

    @property
    def workflow_metadata(self) -> WorkflowMetadata | None:
        return self._workflow_metadata

    def _set_workflow_context(self, workflow_input: WorkflowInput, workflow_metadata: WorkflowMetadata) -> None:
        self._workflow_input = workflow_input
        self._workflow_metadata = workflow_metadata

    @abstractmethod
    def _logic(self) -> None:
        raise NotImplementedError()

    @property
    def current_execution(self) -> NodeExecution:
        return self._executions[-1]

    @property
    def last_execution(self) -> NodeExecution:
        return self._executions[-1]

    @property
    def attempt(self) -> int:
        return len(self._executions)

    def execute(self) -> None:
        while self.attempt <= self.max_retries:
            try:
                self._start_node_execution()
                self.on_start()

                self._run_with_timeout()
                self.on_success()
                break
            except Exception as e:
                self.on_failure(e)
                if not self._handle_retry(e):
                    raise e
            finally:
                self._finalize_node_execution()
                self.on_finish()

    def _create_execution(self) -> NodeExecution:
        return NodeExecution()

    def _start_node_execution(self):
        execution = self._create_execution()
        execution.metadata.start_time = datetime.now()
        execution.status = StatusCodes.IN_PROGRESS
        self._executions.append(execution)

    def _run_with_timeout(self) -> None:
        result: list[Exception | None] = [None]

        def runner():
            try:
                self._logic()
            except Exception as e:
                result[0] = e

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        thread.join(timeout=self.timeout_seconds)

        if thread.is_alive():
            self._handle_exception(TimeoutException())

        if result[0] is not None:
            self._handle_exception(result[0])

    def _handle_retry(self, error: Exception) -> bool:
        if self.attempt >= self.max_retries:
            self._logger.error(f"{self.name} failed: {error}. Retries exhausted.")
            return False

        self._logger.warning(f"{self.name} failed: {error}. Retrying in {self.retry_delay_seconds}s...")
        time.sleep(self.retry_delay_seconds)
        return True

    def _finalize_node_execution(self) -> None:
        current = self.current_execution

        if current.metadata.end_time is None:
            current.metadata.end_time = datetime.now()

        if current.status == StatusCodes.IN_PROGRESS:
            current.status = StatusCodes.COMPLETED

    def _handle_exception(self, exception: Exception | WorkflowException | None) -> None:
        if exception is None:
            return

        current = self.current_execution
        status = exception.exit_code if isinstance(exception, WorkflowException) else StatusCodes.FAILED
        current.status = status
        current.error = NodeError(
            status=status,
            exception_class_name=exception.__class__.__name__,
            exception_message=str(exception),
        )
        raise exception

    def on_start(self) -> None:
        """Called when a node execution starts."""
        pass

    def on_success(self) -> None:
        """Called when a node execution completes successfully."""
        pass

    def on_failure(self, error: Exception) -> None:
        """Called when a node execution fails."""
        pass

    def on_finish(self) -> None:
        """Called at the end of any node execution (success or failure)."""
        pass


    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Node):
            return NotImplemented

        if other is self:
            return True
