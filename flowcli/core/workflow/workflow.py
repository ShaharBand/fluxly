import sys
import threading
import time
from collections.abc import Callable
from datetime import datetime
from typing import Annotated
from uuid import uuid4

from pydantic import BaseModel, Field, PrivateAttr

from flowcli.core.docs_generator.generator import generate_workflow_documentation
from flowcli.core.exceptions import TimeoutException, WorkflowException
from flowcli.core.node.node import Node
from flowcli.core.status import StatusCodes
from flowcli.core.workflow.exceptions import (
    NodesNotFoundException,
    UnsupportedGraphScenario,
)
from flowcli.core.workflow.execution import WorkflowExecution
from flowcli.core.workflow.graph import WorkflowGraph
from flowcli.core.workflow.input import WorkflowInput
from flowcli.core.workflow.metadata import WorkflowMetadata
from flowcli.core.workflow.utils import build_cli_command_from_workflow_input
from flowcli.services import LoggerConfig, LoggerService


class Workflow(BaseModel):
    name: Annotated[str, Field(max_length=64, min_length=2, description="The name of the workflow.")]
    description: Annotated[str | None, Field(max_length=128, min_length=3, description="The description of the workflow.")] = None
    version: Annotated[str | None, Field(description="The workflow version.")] = None
    inputs: Annotated[WorkflowInput | None, Field(description="The workflow inputs.")] = None

    _id: str = PrivateAttr(default_factory=lambda: str(uuid4()))
    _executions: list[WorkflowExecution] = PrivateAttr(default_factory=list)
    _graph: WorkflowGraph = PrivateAttr(default_factory=WorkflowGraph)
    _execution_groups: list[set[str]] = PrivateAttr(default_factory=list)
    _logger: LoggerService = PrivateAttr(default_factory=lambda: LoggerService(config=LoggerConfig()))

    @property
    def id(self) -> str:
        return self._id

    @property
    def current_execution(self) -> WorkflowExecution:
        return self._executions[-1]

    @property
    def last_execution(self) -> WorkflowExecution:
        return self._executions[-1]

    @property
    def attempt(self) -> int:
        return len(self._executions)

    @property
    def metadata(self) -> WorkflowMetadata:
        return self.current_execution.metadata

    def init_by_cli(self) -> None:
        try:
            self.execute()
        finally:
            if self.last_execution:
                sys.exit(self.last_execution.status.value)
            else:
                sys.exit(1)

    def add_node(self, node: Node) -> None:
        self._graph.add_node(node)

    def add_edge(self, source_node: Node, dest_node: Node) -> None:
        self._graph.add_edge(source_node, dest_node)

    def add_conditional_edge(self, source_node: Node, dest_node: Node, condition: Callable[[], bool]) -> None:
        self._graph.add_conditional_edge(source_node, dest_node, condition)

    def add_execution_group(self, nodes: list[Node]) -> None:
        if not nodes:
            raise ValueError("Execution group must include at least one node.")

        node_names = {node.name for node in nodes}
        missing_nodes = node_names - self._graph.nodes.keys()
        if missing_nodes:
            raise ValueError(f"Execution group contains unknown nodes: {sorted(missing_nodes)}")

        self._execution_groups.append(node_names)

    def get_nodes(self) -> list[Node]:
        return list(self._graph.nodes.values())

    def get_execution_groups(self) -> list[set[str]]:
        return [group.copy() for group in self._execution_groups]

    def _create_execution(self) -> WorkflowExecution:
        return WorkflowExecution(id=str(self.attempt + 1))

    def _all_execution_groups_dead(self) -> bool:
        nodes = self._graph.nodes
        groups = self._execution_groups or [set(nodes.keys())]

        for group in groups:
            group_failed = any(
                (nodes[n].attempt > 0 and nodes[n].last_execution.status != StatusCodes.COMPLETED)
                for n in group if n in nodes
            )
            if not group_failed:
                return False

        return True

    def execute(self) -> None:
        try:
            if not self._graph.nodes:
                raise NodesNotFoundException

            self._log_workflow_start()
            while self.attempt <= self.inputs.max_retries:
                try:
                    self._start_workflow_execution()
                    self.on_start()

                    self._run_with_timeout()
                    self.on_success()
                    break
                except Exception as e:
                    self.on_failure(e)
                    if not self._handle_retry(e):
                        raise e
                finally:
                    self._finalize_workflow_execution()
                    self.on_finish()

        finally:
            self._finalize_workflow()

    def _start_workflow_execution(self) -> None:
        execution = self._create_execution()
        execution.metadata.start_time = datetime.now()
        execution.status = StatusCodes.IN_PROGRESS
        self._executions.append(execution)

    def _run_with_timeout(self) -> None:
        result: list[Exception | bool] = []

        def runner() -> None:
            try:
                self._iterate_nodes()
                result.append(True)
            except Exception as e:
                result.append(e)

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        thread.join(timeout=self.inputs.timeout_seconds)

        if thread.is_alive():
            self._handle_exception(TimeoutException())

        if result and isinstance(result[0], Exception):
            self._handle_exception(result[0])

    def _handle_exception(self, exception: Exception | WorkflowException | None) -> None:
        if exception is None:
            return
        current = self.current_execution
        status = exception.exit_code if isinstance(exception, WorkflowException) else StatusCodes.FAILED
        current.status = status
        raise exception

    def _handle_retry(self, error: Exception) -> bool:
        if self.attempt >= self.inputs.max_retries:
            self._logger.error(f"{self.name} failed: {error}. Retries exhausted.")
            return False

        self._logger.warning(f"{self.name} failed: {error}. Retrying in {self.inputs.retry_delay_seconds}s...")
        time.sleep(self.inputs.retry_delay_seconds)
        return True

    def _finalize_workflow_execution(self) -> None:
        current = self.current_execution

        if current.metadata.end_time is None:
            current.metadata.end_time = datetime.now()

        if current.status == StatusCodes.IN_PROGRESS:
            current.status = StatusCodes.COMPLETED

    def _finalize_workflow(self) -> None:
        self._log_workflow_summary()

        if self.inputs.auto_generate_md:
            generate_workflow_documentation(
                workflow=self,
                md_output_path=self.inputs.md_file_path,
                diagram_output_path=self.inputs.diagram_file_path,
            )

    def _iterate_nodes(self) -> None:
        all_nodes: list[Node] = list(self._graph.nodes.values())
        running_threads: dict[str, threading.Thread] = {}
        scheduled: set[str] = set()
        completed: set[Node] = set()
        node_errors: dict[str, Exception] = {}

        while True:
            runnable = [
                n for n in all_nodes
                if n.name not in scheduled and self._graph.can_node_run(n, completed)
            ]

            for node in runnable:
                children = self._graph.get_children(node)
                if any(child.name in running_threads for child in children):
                    raise UnsupportedGraphScenario("Attempted to start a node while one of its children is running")

                def _target(n: Node) -> None:
                    try:
                        self.run_node(n)
                    except Exception as e:  # noqa: BLE001 - we intentionally capture to decide at workflow level
                        node_errors[n.name] = e

                thread = threading.Thread(target=_target, args=(node,), daemon=True)
                running_threads[node.name] = thread
                scheduled.add(node.name)
                thread.start()

            for name, thread in list(running_threads.items()):
                if thread.is_alive():
                    continue

                thread.join()
                node = self._graph.nodes[name]
                completed.add(node)
                self.current_execution.output.nodes_executions.append(node.last_execution)
                self._log_node_summary(node)
                if node.last_execution.status != StatusCodes.COMPLETED:
                    if self._all_execution_groups_dead():
                        raise node_errors.get(name) or Exception(
                            str(node.last_execution.error) if node.last_execution.error else f"Node {name} failed"
                        )
                del running_threads[name]

            if not running_threads:
                pending_runnable = [
                    n for n in all_nodes
                    if n.name not in scheduled and self._graph.can_node_run(n, completed)
                ]
                if not pending_runnable:
                    break

    def run_node(self, node: Node) -> None:
        node._set_workflow_context(workflow_input=self.inputs, workflow_metadata=self.metadata)

        self._log_node_start(node)
        node.execute()

    def _log_workflow_start(self) -> None:
        if not self.inputs.verbose:
            return

        self._logger.info(f"{'-'*30}\n"
                          f"Executing - Workflow: {self.name}, version: {self.version}\n"
                          f"Command: {build_cli_command_from_workflow_input(self.inputs)}\n"
                          f"Inputs: {self.inputs}\n"
                          f"{'-'*30}")

    def _log_workflow_summary(self) -> None:
        if not self.inputs.verbose:
            return

        latest = self.last_execution
        meta_str, out_str = (str(latest.metadata), str(latest.status)) if latest else ("{}", "{}")

        prev_status_lines = [
            f"  - Attempt #{i}: status={ex.status} duration={ex.metadata.process_time}"
            for i, ex in enumerate(self._executions[:-1], 1)
        ] if self._executions and len(self._executions) > 1 else []

        prev_section = f"Previous executions:\n{chr(10).join(prev_status_lines)}\n" if prev_status_lines else ""

        self._logger.info(f"{'-'*30}\n"
                          f"Summary - Workflow: {self.name} - Attempt #{self.attempt}\n"
                          f"Metadata: {meta_str}\n"
                          f"Output: {out_str}\n"
                          f"{prev_section}"
                          f"{'-'*30}")

    def _log_node_start(self, node: Node) -> None:
        if not self.inputs.verbose:
            return

        self._logger.info(f"{'-'*30}\n"
                          f"Executing - Node: {node.name}\n"
                          f"Node Configuration:\n"
                          f"Timeout Seconds: {node.timeout_seconds}\n"
                          f"Retries: {node.max_retries}, Retry Delay Seconds: {node.retry_delay_seconds}\n"
                          f"{'-'*30}")

    def _log_node_summary(self, node: Node) -> None:
        latest = node.last_execution if node.last_execution else None
        if not self.inputs.verbose:
            status = latest.status if latest else StatusCodes.UNKNOWN
            duration = latest.metadata.process_time if latest else None
            if status == StatusCodes.COMPLETED:
                self._logger.info(f"Node {node.name} completed in {duration}")
            else:
                err_cls = latest.error.exception_class_name if latest and latest.error else None
                err_msg = latest.error.exception_message if latest and latest.error else None
                self._logger.info(
                    f"Node {node.name} failed ({status.name}) in {duration} error={err_cls}: {err_msg}"
                )
            return

        meta, out, err = (
            (str(latest.metadata), str(latest.output), str(latest.error))
            if latest else ("{}", "{}", "{}")
        )

        prev_failures = [
            f"\t\t- Attempt #{i}: status={ex.status} duration={ex.metadata.process_time} "
            f"error={ex.error.exception_class_name if ex.error else None}: "
            f"{ex.error.exception_message if ex.error else None}"
            for i, ex in enumerate(node.executions[:-1], 1)
            if ex.status != StatusCodes.COMPLETED
        ]
        prev_failures_str = '\n'.join(prev_failures)

        prev_section = (
            f"Previous execution failures:\n{prev_failures_str}\n"
            if prev_failures else ""
        )

        self._logger.info(
            f"{'-'*30}\n"
            f"Summary - Node: {node.name} - Execution #{node.attempt}\n"
            f"Metadata: {meta}\n"
            f"Output: {out}\n"
            f"Error: {err}\n"
            f"{prev_section}"
            f"{'-'*30}"
        )

    def on_start(self) -> None:
        """Called when a workflow execution starts."""
        pass

    def on_success(self) -> None:
        """Called when a workflow execution completes successfully."""
        pass

    def on_failure(self, error: Exception) -> None:
        """Called when a workflow execution fails."""
        pass

    def on_finish(self) -> None:
        """Called at the end of any workflow execution (success or failure)."""
        pass
