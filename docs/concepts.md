Fluxly revolves around a few central abstractions that let you build **typed, maintainable, and DAG-based workflows**.

---

## Workflow

A `Workflow` represents a **DAG of nodes**, including metadata, inputs, execution history, and orchestration logic.

!!! note "Workflow Responsibilities"
    - Maintain a graph of nodes and their dependencies.
    - Execute nodes respecting DAG constraints.
    - Track executions and statuses.
    - Generate documentation and diagrams if enabled.

!!! code "Workflow Example"
    ```python
    from fluxly.workflow import Workflow

    wf = Workflow(name="demo-workflow", description="Demo workflow")
    ```

---

## WorkflowInput

`WorkflowInput` defines **typed inputs** for a workflow.  

!!! note "Typed Inputs"
    - Uses Pydantic for validation.
    - Drives **CLI flag generation and API payload validation**, including defaults, type hints, and descriptions.
    - Accessible to all nodes via `self.workflow_input`.

!!! code "WorkflowInput Example"
    ```python
    from fluxly.workflow import WorkflowInput

    class MyInput(WorkflowInput):
        message: str = "Hello"
        repeat: int = 3
    ```

---

## Node

A `Node` represents a **single unit of work** in a workflow.

!!! note "Node Responsibilities"
    - Encapsulate logic via `_logic()`.
    - Track execution attempts, status, and errors.
    - Supports `timeout_seconds`, `max_retries`, and `retry_delay_seconds`.
    - Integrates lifecycle hooks (`on_start`, `on_success`, `on_failure`, `on_finish`).

!!! code "Node Example"
    ```python
    from fluxly.node import Node

    class PrintNode(Node):
        @property
        def workflow_input(self) -> MyInput:
            return self._workflow_input

        def _logic(self) -> None:
            for i in range(self.workflow_input.repeat):
                self._logger.info(f"{i+1}: {self.workflow_input.message}")
    ```

---

## Node-to-Node Communication

Nodes communicate via **typed execution classes**, either by:
- Importing and referencing the upstream node instance after it ran
- Using a **conditional edge** that checks upstream `last_execution`

Each node typically lives in its own file; import node classes and create instances in the workflow.

!!! code "producer.py"
    ```python
    from fluxly.node import Node, NodeExecution, NodeOutput

    class ProducerOutput(NodeOutput):
        value: int | None = None

    class ProducerExecution(NodeExecution):
        output: ProducerOutput = ProducerOutput()

    class Producer(Node):
        def _create_execution(self) -> ProducerExecution:
            return ProducerExecution()

        def _logic(self) -> None:
            self.current_execution.output.value = 42
    ```

!!! code "consumer.py"
    ```python
    from fluxly.node import Node

    from producer import Producer

    class Consumer(Node):
        producer: Producer

        def _logic(self) -> None:
            value = self.producer.last_execution.output.value
            self._logger.info(value)
    ```

!!! code "workflow.py"
    ```python
    from fluxly.workflow import Workflow

    from producer import Producer
    from consumer import Consumer

    wf = Workflow(name="demo")
    producer = Producer(name="producer")
    consumer = Consumer(name="consumer", producer=producer)

    wf.add_node(producer)
    wf.add_node(consumer)
    wf.add_edge(producer, consumer)
    ```

!!! code "Conditional edge based on upstream status"
    ```python
    from fluxly.workflow import Workflow
    from fluxly.status import StatusCodes

    wf = Workflow(name="demo")
    producer = Producer(name="producer")
    consumer = Consumer(name="consumer")

    wf.add_node(producer)
    wf.add_node(consumer)

    # Run consumer only if producer completed successfully and produced a value
    wf.add_conditional_edge(
        producer,
        consumer,
        condition=lambda: (
            producer.last_execution.status == StatusCodes.COMPLETED
            and producer.last_execution.output.value is not None
        ),
    )
    ```

---

## Execution Groups

Execution groups define **sets of nodes**, where the workflow is considered **successful if at least one group succeeds**.  

Even after a group succeeds, the **workflow continues running** until **no new runnable nodes** remain (i.e., all reachable dependencies are exhausted).

!!! note "Execution Groups"
    - Default: all nodes belong to a single group.  
    - Any group’s success marks the workflow as successful.  
    - Execution continues until all reachable nodes are finished.  
    - Enables **partial success tolerance** for fault-tolerant workflows.

!!! code "Execution Group Example"
    ```python
    workflow.add_execution_group([node_a, node_b])
    workflow.add_execution_group([node_c])
    ```

---

## Edges and Conditional Edges

Edges define **dependencies between nodes**. Conditional edges execute only if the **condition function evaluates True**, which can check the **last execution status** of a node.

!!! code "Edges Example"
    ```python
    workflow.add_edge(node_a, node_b)  # node_b runs after node_a
    workflow.add_conditional_edge(
        node_b,
        node_c,
        condition=lambda: node_b.last_execution.status == StatusCodes.COMPLETED
    )
    ```

!!! code "Edge that runs only if source completed"
    ```python
    workflow.add_edge_if_source_completed(node_a, node_b)
    ```

---

## Wrapping & Extensibility

Workflows and nodes can be **wrapped or subclassed** to add:

- Logging and metrics
- Policy enforcement
- Integrations with external services
- Retry or error-handling strategies

!!! code "Extensibility Example"
    ```python
    class LoggingNode(PrintNode):
        def on_start(self) -> None:
            self._logger.info(f"Starting {self.name}")

        def on_success(self) -> None:
            self._logger.info(f"Finished {self.name}")

        def on_failure(self, error) -> None:
            self._logger.info(f"{self.name} failed: {error}")
    ```

This enables **consistent cross-cutting behavior** without modifying core business logic.

---

## Lifecycle Hooks

Fluxly nodes provide **lifecycle hooks** that let you add custom behavior at key points of execution without modifying `_logic()`.  

!!! note "Available Hooks"
    - `on_start` – called before `_logic()` runs.
    - `on_success` – called after `_logic()` completes successfully.
    - `on_failure` – called if `_logic()` raises an exception.
    - `on_finish` – always called at the end of execution.

!!! code "Hooks Example"
    ```python
    from fluxly.node import Node

    from my_input import MyInput

    class LoggingNode(Node):
        @property
        def workflow_input(self) -> MyInput:
            return self._workflow_input

        def _logic(self) -> None:
            self._logger.info(f"Running logic for {self.name}")

        def on_start(self) -> None:
            self._logger.info(f"Starting node: {self.name}")

        def on_success(self) -> None:
            self._logger.info(f"Node succeeded: {self.name}")

        def on_failure(self, error) -> None:
            self._logger.info(f"Node failed: {self.name} with error {error}")

        def on_finish(self) -> None:
            self._logger.info(f"Finished execution for node: {self.name}")
    ```

---

## NodeExecution & WorkflowExecution

Fluxly allows you to **customize the execution structure** by overriding how executions, outputs, and metadata are created.  
This lets you inject custom behavior, logging, or extended data without modifying the core node logic.


**Default Execution Structure:**

- **NodeExecution** wraps:
  - `metadata` → `NodeMetadata` (start/end times, computed duration)
  - `status` → `StatusCodes` (WAITING, IN_PROGRESS, COMPLETED, FAILED)
  - `output` → `NodeOutput` (data produced by `_logic()`)
  - `error` → `NodeError` (if the execution fails)

- **WorkflowExecution** aggregates:
  - `metadata` → `WorkflowMetadata` (workflow start/end times, execution summary)
  - `output` → Workflow-level output dictionary
  - Status derived from node executions and execution groups

!!! note "Custom Execution"
    By overriding `_create_execution()` on a Node, you can use a custom subclass of `NodeExecution` that stores extra info (e.g., logs, intermediate metrics).

Example:

!!! code "custom_execution.py"
    ```python
    from pydantic import BaseModel
    from fluxly.node import NodeExecution, NodeMetadata

    # Custom output for this node
    class CustomNodeOutput(BaseModel):
        result_text: str | None = None

    # Custom execution with typed metadata and output
    class CustomNodeExecution(NodeExecution):
        metadata: NodeMetadata = NodeMetadata()
        output: CustomNodeOutput = CustomNodeOutput()
    ```

Using Custom Execution:

!!! code "custom_node.py"
    ```python
    from fluxly.node import Node

    import CustomNodeExecution, CustomNodeOutput

    class CustomNode(Node):
        @property
        def current_execution(self) -> CustomNodeExecution:
            return super().current_execution

        @property
        def last_execution(self) -> CustomNodeExecution:
            return super().last_execution

        def _create_execution(self) -> CustomNodeExecution:
            return CustomNodeExecution()

        def _logic(self) -> None:
            self.current_execution.output.result_text = f"processed{suffix}"
            self._logger.info(f"CustomNode produced: {self.current_execution.output.result_text}")
    ```

!!! note "Benefits of Custom Execution & Metadata"
    - `metadata.start_time` and `metadata.end_time` are tracked automatically.
    - Output fields are fully typed for IDE and type-checker support.
    - Custom execution enables **per-node outputs and richer metadata**.
    - Facilitates advanced workflows with typed inspection and logging.

