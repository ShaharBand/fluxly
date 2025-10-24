FluxCLI is a **CLI-first framework** for designing, running, and shipping DAG-based workflows with **strong typing, lifecycle hooks, and maintainable code structure**. It’s built for developers who want **predictable, debuggable, and production-ready workflows**.

---

## CLI-first, strongly typed

Each workflow becomes a CLI command. Flags are auto-generated from your `WorkflowInput` types, including **type hints, defaults, and descriptions**.  
This eliminates manual parsing and ensures **consistent interfaces across scripts and production pipelines**.

!!! code "CLI Example"
    ```python
    from fluxcli import FluxCLI
    from fluxcli.workflow import Workflow, WorkflowInput
    from fluxcli.node import Node

    class MyInput(WorkflowInput):
        message: str = "hello"

    class Echo(Node):
        _workflow_input: MyInput
        def _logic(self):
            print(f"Message: {self._workflow_input.message}")

    cli = FluxCLI()
    cli.add_command("echo-msg", lambda: Workflow("echo-demo"), MyInput)
    cli.run()
    ```

---

## Modern Python throughout

Workflows and nodes are implemented using **idiomatic Python classes and type annotations**.  
No DSLs or YAML schemas are required—use **Pydantic** for input validation and serialization.

!!! code "Type-safe Node Example"
    ```python
    class CounterInput(WorkflowInput):
        count: int = 5

    class Counter(Node):
        _workflow_input: CounterInput
        def _logic(self):
            for i in range(self._workflow_input.count):
                print(f"Step {i+1}")
    ```

---

## Node-to-node communication

Nodes communicate via **typed execution outputs**, not ad-hoc dictionaries or positional references.  
This ensures **clear boundaries, maintainability, and debuggability**.

!!! code "Node Communication"
    ```python
    class OutputNode(Node):
        def _logic(self):
            return {"result": 42}

    class ConsumerNode(Node):
        def _logic(self, output_from_previous: dict):
            print(output_from_previous["result"])
    ```

---

## DAG orchestration with validation and retries

Workflows are automatically validated as DAGs.  
Execution respects dependencies and conditional edges. **Retries and timeouts** keep workflows robust.

!!! code "DAG Example"
    ```python
    wf = Workflow("demo")

    node_a = Echo(name="A", timeout_seconds=5)
    node_b = Echo(name="B")
    node_c = Echo(name="C")

    wf.add_node(node_a)
    wf.add_node(node_b)
    wf.add_node(node_c)

    wf.add_edge(node_a, node_b)  # B runs after A
    wf.add_conditional_edge(node_b, node_c, condition=lambda: True)
    ```

---

## Lifecycle hooks

Add cross-cutting behavior **without touching business logic**.  
Hooks exist at both **node and workflow levels**:

- `on_start` – before execution  
- `on_success` – after success  
- `on_failure` – after failure  
- `on_finish` – always called

!!! code "Logging Example"
    ```python
    class Echo(Node):
        def on_start(self):
            print(f"Starting {self.name}")

        def on_success(self):
            print(f"Finished {self.name}")
    ```

---

## Typed exceptions and consistent exit codes

- Raise **custom exceptions** mapped to `StatusCodes`.
- CLI and schedulers always receive consistent exit codes.
- Makes **CI/CD pipelines predictable**.

!!! code "Exception Example"
    ```python
    from fluxcli.core.exceptions import WorkflowException
    from fluxcli.core.status import StatusCodes

    class MyNode(Node):
        def _logic(self):
            raise WorkflowException("Something went wrong", exit_code=StatusCodes.FAILURE)
    ```

---

## Auto-generated documentation and diagrams

FluxCLI can generate **Markdown documentation** and **DAG diagrams** automatically.  
Helps teams **review workflow structures** and share knowledge.

!!! note "Simple workflow"
    ![Simple workflow](imgs/simple_workflow.png)
    *Clear, linear steps for quick tasks.*

!!! note "Complex workflow"
    ![Complex workflow](imgs/complex_workflow.png)
    *Branching, conditional edges, and parallel paths stay readable.*

---

## Extensible architecture

- Wrap workflows and nodes to add **logging, metrics, policies, integrations**.
- Define a **base layer** for shared defaults and configuration.
- Scale from **local scripts to production pipelines** with minimal rewrites.

---

## Tested and type-checked

- Unit tests cover workflow behavior.
- Continuous integration enforces **linting, type-checks, and formatting**.
- Strong typing ensures **safe refactors** and long-term maintainability.
