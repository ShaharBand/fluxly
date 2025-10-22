<div align="center">
  <img src="./docs/imgs/logo.png" 
       style="max-width: 250px;" 
       alt="FlowCLI Logo" 
       title="FlowCLI Logo">


![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)

FlowCLI - Lightweight, CLI-first framework for building **directed acyclic graph (DAG)**-based workflows.

</div>

---

FlowCLI is a lightweight framework for building and running **DAG-based workflows**.  
Each workflow is defined as a **graph of command-line actions**, and the entire graph itself becomes a **single CLI command**.

This design makes workflows fully **self-contained**:

- Run them locally as normal CLI tools.
- Wrap them in Docker images for portability.
- Plug them into higher-level orchestrators (Argo, Airflow, Prefect, CI/CD) without extra glue code.

With FlowCLI, pipelines are **highly structured** for safer execution, cleaner debugging, and better modularity.  
Flows can run standalone or as part of a larger system, making FlowCLI both lightweight and flexible.

---

<img src="docs/imgs/complex_workflow.png" alt="Complex Workflow Diagram" title="Complex Workflow Diagram" style="max-width: 700px; width: 100%;" />

---

## Table of Contents

- [1. Key Features](#1-key-features)
- [2. Technology Stack](#2-technology-stack)
- [3. Installation](#3-installation)
- [4. Guide](#4-guide)
  - [4.1. Minimal Example](#41-minimal-example)
  - [4.2. Core Concepts](#42-core-concepts)
    - [Workflow](#workflow)
    - [Node](#node)
    - [Node-to-Node Communication](#node-to-node-communication)
    - [Execution Groups](#execution-groups)
    - [Orchestration Controls](#orchestration-controls)
    - [Wrapping & Extensibility](#wrapping--extensibility)
  - [4.3. Lifecycle Hooks](#43-lifecycle-hooks)
    - [Node hooks](#node-hooks)
    - [Workflow hooks](#workflow-hooks)
  - [4.4. Custom Exceptions and Exit Codes](#44-custom-exceptions-and-exit-codes)
  - [4.5. Typed executions: custom output/metadata](#45-typed-executions-custom-outputmetadata)
- [5. Auto-generated Documentation & Diagrams](#5-auto-generated-documentation--diagrams)
- [6. WorkflowInput Flags for CLI & Docs](#6-workflowinput-flags-for-cli--docs)
- [7. Demo](#7-demo)

---

## 1. Key Features

- **CLI-based actions** – every node has a clear interface for inputs and outputs.
- **DAG-based workflows** – define arbitrary connections between tasks and their dependencies.
- **Highly structured workflows** – strict validation ensures safer pipelines, easier debugging, and predictable behavior.
- **Self-orchestrated nodes** – each graph workflow manages its own execution order, retries, and dependencies.
- **Lightweight building blocks** – graph workflows are small, self-contained units that can each run in their own environment.
- **Extensible by design** – wrap graph workflows with your own classes to add logging, metrics, or integrations.
- **Local-first development** – debug and run workflows as simple CLIs, then scale them seamlessly to CI/CD or external orchestrators.

---

## 2. Technology Stack

- [**Pydantic**](https://github.com/pydantic/pydantic): Strict data validation and schema for inputs/outputs.
- [**Typer**](https://github.com/fastapi/typer): Easy wrapper for building great CLIs.
- [**Diagrams**](https://github.com/mingrammer/diagrams): Auto-generate DAG diagrams as code.
- [**Pixi**](https://github.com/prefix-dev/pixi): Cross-platform package and environment management.
- [**Ruff**](https://github.com/charliermarsh/ruff): Lightning-fast linting.
- [**Mypy**](https://github.com/python/mypy): Static type checking for Python, enforcing type safety and correctness.
- [**Coverage.py**](https://github.com/nedbat/coveragepy): Measures code coverage of tests for quality assurance.
- [**Pytest**](https://github.com/pytest-dev/pytest): Testing framework.
- **GitHub CI/CD**: Continuous integration and deployment.

---

## 3. Installation

Install with `pip`:

```bash
pip install flowcli
```

---

## 4. Guide

### 4.1. Minimal Example

CLI Entrypoint based on workflows:

```python
from flowcli import FlowCLI
from my_project.workflows import MyWorkflow, MyWorkflowInput


if __name__ == "__main__":
    cli = FlowCLI()
    cli.add_command("my-workflow", MyWorkflow, MyWorkflowInput)
    cli.run()
```

Then you can run it by using:

```bash
python cli.py my-workflow [--flags]
```

### 4.2. Core Concepts

#### Workflow
Workflows hold a DAG of `Node`s with edges and manage overall execution, retries, and logs.

```python
from flowcli.workflow import Workflow, WorkflowInput

class MyInput(WorkflowInput):
    message: str = "world"

def build_workflow() -> Workflow:
    wf = Workflow(name="demo", description="Demo flow", version="0.1")
    alpha = Echo(name="alpha", description="prints a message", timeout_seconds=5)
    wf.add_node(alpha)
    return wf
```

#### Node
Nodes encapsulate executable logic, retries, and timeouts. Implement `_logic()` and let the framework handle execution bookkeeping.

```python
from flowcli.node import Node

class Echo(Node):
    _workflow_input: MyInput

    @property
    def workflow_input(self) -> MyInput:
        return self._workflow_input

    def _logic(self) -> None:  
        print(f"Echo: {self.workflow_input.message}")
```

Edges can be unconditional or conditional:

```python
wf.add_edge(alpha, beta)
wf.add_conditional_edge(alpha, beta, condition=lambda: alpha.last_execution.output.var == "example")
```

Execution:
- Programmatic: `wf.execute()`
- CLI: use `FlowCLI` and run your CLI file, e.g. `python path/to/cli.py my-workflow --message hi`

#### Node-to-Node Communication

- Nodes are intentionally isolated. 
- Communication happens by reading other nodes’ execution outputs only. 
- Do not call other nodes directly or share mutable state.
- Inside workflow wiring, use conditional edges that close over node instances and inspect their outputs:

```python
wf.add_conditional_edge(alpha, beta, condition=lambda: alpha.last_execution.output.var == "example")
```

- Inside a node’s `_logic`, avoid reaching to other running nodes. Use the workflow DAG and conditions to express data/control dependencies.
- After a node run, you can read outputs by importing the node instances you created in the builder module and accessing `node.last_execution.output` for reporting/post-processing.

#### Execution Groups

Execution groups let you define alternative success criteria: if any one group completes fully, the workflow is considered successful.

```python
wf.add_execution_group([alpha, beta])
wf.add_execution_group([gamma, delta])
# If either {alpha,beta} or {gamma,delta} all complete successfully, the workflow succeeds
```

Notes:
- Groups are sets of node names; a default implicit group is all nodes when none are defined.
- Groups work alongside the DAG; dependencies and conditions still apply within each group.

#### Orchestration Controls

You can tune reliability and timing at both node and workflow levels:

- Node level: `timeout_seconds`, `max_retries`, `retry_delay_seconds`
- Workflow level (via `WorkflowInput`): `timeout_seconds`, `max_retries`, `retry_delay_seconds`

These settings determine how long steps may run, how many times they retry, and their backoff delay. Timeouts raise framework exceptions which are surfaced in execution status and logs.

#### Wrapping & Extensibility

Wrapping is straightforward. Nodes and workflows are Pydantic models with clear lifecycle hooks.

- Create thin wrappers/subclasses to add logging, metrics, or cross-cutting concerns.
- Compose nodes in higher-level factories that set defaults, inject configs, or attach common edges.
- Extend `WorkflowInput` with your own fields; the CLI generator will expose them automatically.

### 4.3. Lifecycle Hooks

Use hooks to add logging, metrics, cleanup, or side-effects without cluttering core logic.

#### Node hooks

- `on_start()`: called right after an execution attempt begins, before `_logic()` runs.
- `on_success()`: called after `_logic()` completes without raising.
- `on_failure(error: Exception)`: called when `_logic()` raises or a timeout occurs.
- `on_finish()`: called at the end of every attempt (success or failure), even if an exception was raised.

Behavioral notes:
- Retries: `execute()` loops attempts up to `max_retries`, invoking the hook sequence for each attempt.
- Timeouts: a timeout raises a framework exception and flows through `on_failure()`; the attempt is marked failed.
- Telemetry: use hooks to emit per-attempt logs/metrics, referencing `self.current_execution` for metadata/output/error.

#### Workflow hooks

- `on_start()`: called when a workflow execution attempt starts.
- `on_success()`: called after the DAG finishes successfully for the attempt.
- `on_failure(error: Exception)`: called when any unhandled error propagates from node execution.
- `on_finish()`: called at the end of the attempt (success or failure).

Behavioral notes:
- Retries: workflow attempts are retried up to `inputs.max_retries`, with hooks invoked per attempt.
- Timeout: the workflow run happens in a managed thread; if it exceeds `inputs.timeout_seconds`, a timeout is raised and `on_failure()` is invoked.
- Finalization: after all attempts, final summary logging and optional documentation/diagram generation are performed.

### 4.4. Custom Exceptions and Exit Codes

FlowCLI provides typed exceptions to give you precise exit-code and status control. Raise these from inside nodes (or workflows) to set both the runtime status and the process exit code in a consistent way.

Built-ins (all inherit from `WorkflowException` and map to `StatusCodes`):
- `TimeoutException` → `StatusCodes.TIMED_OUT`
- `InfrastructureErrorException` → `StatusCodes.INFRASTRUCTURE_ERROR`
- `DataErrorException` → `StatusCodes.DATA_ERROR`
- `PrerequisiteFailureException` → `StatusCodes.PREREQUISITE_FAIL`
- `APICallFailureException` → `StatusCodes.API_CALL_FAILURE`
- `NetworkFailureException` → `StatusCodes.NETWORK_FAILURE`
- `DataValidationFailureException` → `StatusCodes.DATA_VALIDATION_FAILURE`
- `DependencyUnavailableException` → `StatusCodes.DEPENDENCY_UNAVAILABLE`

Usage inside a node:

```python
from flowcli.exceptions import DataValidationFailureException

class Validate(Node):
    def _is_valid_input(self) -> bool:
        return False

    def _logic(self) -> None:
        if not self._is_valid_input():
            raise DataValidationFailureException("Invalid input payload")
```

Custom domain exceptions:

```python
from enum import Enum

from flowcli.exceptions import WorkflowException
from flowcli.status import StatusCodes

# Prefer mapping to built-in StatusCodes for consistent statuses
class BusinessRuleViolation(WorkflowException):
    exit_code: Enum = StatusCodes.DATA_ERROR
```

Rules and behavior:
- Exit codes are validated (0–255) and must be Enum values; use `StatusCodes` to align node/workflow status with the exit code.
- When a `WorkflowException` is raised:
  - Node attempt is marked with that status; `node.last_execution.status` reflects it and the error is recorded.
  - The workflow aggregates errors and propagates the status; final process exit uses the configured code.
- Timeouts and retries apply before the final status is set based on the last attempt.

Tip: keep your exception taxonomy small and map business failures onto an appropriate `StatusCodes` value to make CI/CD exit-code handling and dashboards consistent.

### 4.5. Typed executions: custom output/metadata

FlowCLI models node/workflow attempts as execution objects. Communication between nodes happens through these executions (e.g., reading another node's `last_execution.output`).

#### Node: custom `NodeOutput`/`NodeMetadata` and `_create_execution`

```python
from typing import Annotated

from pydantic import Field

from flowcli.node import Node, NodeExecution, NodeMetadata, NodeOutput


class MyNodeOutput(NodeOutput):
    rows_processed: Annotated[int, Field(ge=0, description="Number of rows handled")]
    sample_id: Annotated[str | None, Field(description="Optional sample identifier")] = None


class MyNodeExecution(NodeExecution):
    # Narrow output/metadata types for this node's attempts
    output: MyNodeOutput = MyNodeOutput(rows_processed=0)
    metadata: NodeMetadata = NodeMetadata()


class MyNode(Node):
    def _logic(self) -> None:
        # ... your logic ...
        self.current_execution.output.rows_processed += 1

    def _create_execution(self) -> MyNodeExecution:  # type: ignore[override]
        return MyNodeExecution()

    # Optional: expose a typed accessor for convenience
    @property
    def last_execution(self) -> MyNodeExecution:  # type: ignore[override]
        return super().last_execution
```

Usage elsewhere (including conditional edges):

```python
alpha = MyNode(name="alpha")

wf.add_conditional_edge(alpha, beta, condition=lambda: alpha.last_execution.output.rows_processed > 100)
```

Notes:
- You can also subclass `NodeMetadata` if you want extra per-attempt fields; set it on the custom execution class similarly to `output`.
- If you prefer not to override `last_execution`, you can keep the base property and cast in your code when needed.

#### Workflow: custom `WorkflowOutput`/`WorkflowMetadata` and `_create_execution`

You can type workflow-level output the same way. This helps when you aggregate per-node results or want to attach summary fields.

```python
from typing import Annotated

from pydantic import Field

from flowcli.workflow import Workflow, WorkflowExecution, WorkflowOutput, WorkflowMetadata
from flowcli.node import NodeExecution


class MyWorkflowOutput(WorkflowOutput):
    succeeded_nodes: Annotated[int, Field(ge=0)] = 0
    failed_nodes: Annotated[int, Field(ge=0)] = 0
    # Optionally narrow the executions list to your custom node executions
    nodes_executions: list[NodeExecution] = []


class MyWorkflowExecution(WorkflowExecution):
    output: MyWorkflowOutput = MyWorkflowOutput()
    metadata: WorkflowMetadata = WorkflowMetadata()


class MyWorkflow(Workflow):
    def _create_execution(self) -> MyWorkflowExecution:  # type: ignore[override]
        return MyWorkflowExecution()

    @property
    def last_execution(self) -> MyWorkflowExecution:  # type: ignore[override]
        return super().last_execution
```

Inside your workflow run, you can update `succeeded_nodes`/`failed_nodes` based on node statuses. Since `Workflow` already appends node executions to `current_execution.output.nodes_executions`, narrowing that field in your custom output provides better suggestions when you read results post-run.

---

## 5. Auto-generated Documentation & Diagrams

FlowCLI can automatically generate a Markdown document and a DAG diagram for your workflow after execution.

- Enable via `WorkflowInput`:
  - `auto_generate_md`: set to `True` to generate docs at the end of the run
  - `md_file_path`: where to write the Markdown file (default: `workflow_documentation.md`)
  - `diagram_file_path`: where to write the DAG diagram image (default: `workflow_diagram.png`)

When enabled, the framework produces a summary of metadata, node executions, and a diagram visualizing nodes and edges.

Example diagram (placeholder):

<img src="./docs/imgs/simple_workflow.png" alt="Workflow Diagram" title="Workflow Diagram" style="max-width: 400px; width: 100%;" />

---

## 6. WorkflowInput Flags for CLI & Docs

`WorkflowInput` fields are used to auto-generate CLI flags and documentation. You can control exposure and presentation using `json_schema_extra`.

Supported extras per field:
- `exclude_from_cli`: if `True`, the field is omitted from the CLI
- `convert_underscores`: if `False`, field name underscores are preserved (default converts to dashes)
- `exclude_from_documentation`: if `True`, the field is omitted from generated docs

Example:

```python
from typing import Annotated
from pydantic import Field

from flowcli.workflow import WorkflowInput


class MyInput(WorkflowInput):
    secret_token: Annotated[str | None, Field(
        default=None,
        description="Authentication token",
        json_schema_extra={"exclude_from_cli": True, "exclude_from_documentation": True},
    )]

    cool_flag: Annotated[bool, Field(
        default=False,
        description="Enable cool stuff",
        json_schema_extra={"convert_underscores": True},
    )]
```

These hints are respected by the CLI generator and the docs generator so your public surface stays clean while retaining powerful, typed inputs.

---

### 7. Demo

We include a structured demo at `examples/structured_demo/cli/app.py` that registers the `structured-demo` command using `FlowCLI`.

```bash
python examples/structured_demo/cli/app.py structured-demo [--flags]
```