# Fluxly — Flexible, Typed DAG Workflows

Fluxly is a **flexible framework** for designing, running, and shipping **DAG-based workflows** with **strong typing, lifecycle hooks, and maintainable code structure**.  
It’s built for developers who want **predictable, debuggable, and production-ready workflows** that can be triggered via **CLI, API, or environment variables**.

---

## Consistent, Strongly Typed Interfaces

Each workflow exposes a **consistent entrypoint**. Inputs from your `WorkflowInput` class are automatically mapped to **CLI flags, API payloads, or environment variables**, including **type hints, defaults, and descriptions**.  
This eliminates manual parsing and ensures **consistent interfaces across scripts and production pipelines**.

!!! code "EntryPoint Example"
    ```python
    from fluxly import Fluxly
    from fluxly.workflow import Workflow, WorkflowInput
    from fluxly.node import Node

    class MyInput(WorkflowInput):
        message: str = "hello"

    class Echo(Node):
        @property
        def workflow_input(self) -> MyInput:
            return self._workflow_input

        def _logic(self) -> None:
            self._logger.info(f"Message: {self.workflow_input.message}")

    app = Fluxly()
    app.add_endpoint("echo-msg", workflow, MyInput)
    app.run()  # CLI, API, or environment triggers
    ```

---

## Modern Python Throughout

Workflows and nodes are implemented using **idiomatic Python classes and type annotations**.  
No DSLs or YAML schemas—use **Pydantic** for input validation and serialization.

!!! code "Type-safe Node Example"
    ```python
    class CounterInput(WorkflowInput):
        count: int = 5

    class Counter(Node):
        @property
        def workflow_input(self) -> CounterInput:
            return self._workflow_input

        def _logic(self) -> None:
            for i in range(self.workflow_input.count):
                self._logger.info(f"Step {i+1}")
    ```

---

## Node-to-Node Communication

Nodes communicate via **typed execution classes**, either by:
- Importing and referencing the upstream node instance after it runs.
- Using **conditional edges** based on upstream status.

Nodes typically live in their own files; import node classes and create instances in the workflow.

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

!!! code "Conditional edge example"
    ```python
    wf.add_edge_if_source_completed(producer, consumer)
    ```

---

## DAG Orchestration with Validation and Retries

Workflows are automatically validated as **DAGs**.  
Execution respects dependencies and conditional edges.

!!! code "DAG Example"
    ```python
    wf = Workflow("demo")

    node_a = Echo(name="A", timeout_seconds=5)
    node_b = Echo(name="B")
    node_c = Echo(name="C")

    wf.add_node(node_a)
    wf.add_node(node_b)
    wf.add_node(node_c)

    wf.add_edge(node_a, node_b)
    wf.add_conditional_edge(node_b, node_c, condition=lambda: True)
    ```

---

## Lifecycle Hooks

Add cross-cutting behavior **without touching business logic**. Hooks exist at **node and workflow levels**:

- `on_start` – before execution  
- `on_success` – after success  
- `on_failure` – after failure  
- `on_finish` – always called

!!! code "Lifecycle Example"
    ```python
    class Echo(Node):
        def on_start(self) -> None:
            self._logger.info(f"Starting {self.name}")

        def on_success(self) -> None:
            self._logger.info(f"Finished {self.name}")
    ```

---

## Typed Exceptions and Consistent Exit Codes

- Raise **custom exceptions** mapped to `StatusCodes`.  
- Entry points (CLI, API, schedulers) receive consistent exit codes.  
- Ensures **predictable CI/CD pipelines**.

!!! code "Exception Example"
    ```python
    from fluxly.exceptions import WorkflowException
    from fluxly.status import StatusCodes

    class MyNode(Node):
        def _logic(self) -> None:
            raise WorkflowException("Something went wrong", exit_code=StatusCodes.FAILURE)
    ```

---

## Auto-Generated Documentation and Diagrams

Fluxly can generate **Markdown documentation** and **DAG diagrams** automatically.  
Helps teams **review workflow structures** and share knowledge.

!!! note "Simple workflow"
    ![Simple workflow](imgs/simple_workflow.png)
    *Clear, linear steps for quick tasks.*

!!! note "Complex workflow"
    ![Complex workflow](imgs/complex_workflow.png)
    *Branching, conditional edges, and parallel paths.*

---

## Extensible Architecture

- Wrap workflows and nodes to add **logging, metrics, policies, integrations**.  
- Define a **base layer** for shared defaults and configuration.  
- Scale from **local scripts to production pipelines** with minimal rewrites.

---

## Tested and Type-Checked

- Unit tests cover workflow behavior.  
- Continuous integration enforces **linting, type-checks, and formatting**.  
- Strong typing ensures **safe refactors** and long-term maintainability.
