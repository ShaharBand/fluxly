<div align="center">
  <img src="imgs/logo.png" alt="Fluxly Logo" title="Fluxly Logo" style="max-width: 200px;" />

  <p>
    <em>Fluxly - Lightweight framework for portable, self-contained <strong>DAG-based workflows</strong>.
    </em>
  </p>

  <p>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
    <a href="https://github.com/ShaharBand/fluxly"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License MIT"></a>
  </p>
</div>

---

**Fluxly** is a lightweight framework for building and running **directed acyclic graph (DAG)-based workflows**.  

The entire workflow acts as a **self-contained execution endpoint**:

- Run them locally or via CLI commands, API calls, or environment triggers.
- Package them in containers for portability.
- Integrate seamlessly with higher-level orchestrators (Argo, Airflow, Prefect, CI/CD) without extra glue code.

With **Fluxly**, pipelines are **highly structured**, enabling safer execution, easier debugging, and better modularity.  
Workflows can run standalone or as part of a larger system, making **Fluxly** both lightweight and flexible.

---

!!! note "Complex workflow"
    <div align="center">
      <img src="imgs/complex_workflow.png" alt="Complex Workflow Diagram" title="Complex Workflow Diagram" style="max-width: 700px; width: 100%;" />
      <p><em>Clear representation of workflow DAG with branching and parallel execution.</em></p>
    </div>

---

## Key Features

- **Flexible entrypoints** – workflows can be triggered via CLI, API calls, or environment variables.
- **DAG-based workflows** – define arbitrary connections between ndoes and their dependencies.
- **Highly structured workflows** – strict validation ensures safer pipelines, easier debugging, and predictable behavior.
- **Self-orchestrated nodes** – each node manages its own execution, retries, and dependencies.
- **Lightweight building blocks** – workflows are self-contained units that can run independently in any environment.
- **Extensible by design** – wrap workflows with custom classes to add logging, metrics, or integrations.
- **Local-first development** – debug and run workflows standalone, then scale seamlessly to CI/CD or external orchestrators.

---

## Installation

!!! code "Install Fluxly"
    ```bash
    pip install fluxly
    ```

---

## Quick Start

### 1) Define Workflow Input

Define a typed `WorkflowInput` to specify all inputs your workflow expects.  
These inputs are **agnostic to how the workflow is triggered** — they can come from **CLI flags, API requests, or environment variables** — giving you maximum flexibility.

!!! code "WorkflowInput Example"
    ```python
    from fluxly.workflow import WorkflowInput

    class MyInput(WorkflowInput):
        message: str = "world"
    ```

### 2) Make nodes

Implement `Node` logic in `_logic()` and type-narrow `workflow_input` for convenience.

!!! code "Node Example"
    ```python
    from fluxly.node import Node

    class Echo(Node):
        @property
        def workflow_input(self) -> MyInput:
            return self._workflow_input

        def _logic(self) -> None:
            self._logger.info(f"Echo: {self.workflow_input.message}")
    ```

### 3) Build a workflow

Create a `Workflow`, add nodes to it, and wire edges/conditions to express execution order and data dependencies.  
Workflows orchestrate retries, timeouts, and overall execution.

!!! code "Workflow Example"
    ```python
    from fluxly.workflow import Workflow

    def build_workflow() -> Workflow:
        wf = Workflow(name="demo", description="Demo flow", version="0.1")

        # Nodes: demonstrate node-level timeout and retries
        alpha = Echo(name="alpha", description="prints a message", timeout_seconds=5, max_retries=1, retry_delay_seconds=1)
        beta = Echo(name="beta", description="prints after alpha")
        gamma = Echo(name="gamma", description="conditional step")

        # Register nodes to the workflow
        wf.add_node(alpha)
        wf.add_node(beta)
        wf.add_node(gamma)

        # Edges (ordering and conditions)
        wf.add_edge(alpha, beta)  # run beta after alpha
        wf.add_conditional_edge(beta, gamma, condition=lambda: True)  # example condition

        return wf
    ```

!!! code "Edge that runs only if source completed"
    ```python
    # Alternatively, run a node only if its parent completed successfully
    wf.add_edge_if_source_completed(alpha, gamma)
    ```
### 4) Expose Your Workflow

Use **Fluxly** to expose your workflow as a single, consistent entrypoint.  
Inputs from your `WorkflowInput` are automatically mapped to **CLI flags, API payloads, or environment variables**, keeping your interface consistent and type-safe across all triggers.

!!! code "Expose Workflow"
    ```python
    from fluxly import Fluxly

    if __name__ == "__main__":
        app = Fluxly()
        wf = build_workflow()
        # register workflow with its input type
        app.add_endpoint("my-workflow", wf, MyInput)
        app.run()  # can be triggered via CLI, API, or env vars
    ```

Run it via CLI:

!!! code "Run CLI"
    ```bash
    python main.py my-workflow --message hello

    # discover generated flags and help text
    python main.py my-workflow --help
    ```

Trigger via **HTTP POST request**:

!!! code "Run via API"
    ```python
    import requests

    url = "http://localhost:8000/my-workflow/run"
    payload = {"message": "hello"}

    response = requests.post(url, json=payload)
    print(response.status_code, response.json())
    ```

Trigger via **environment variables** (with `FLUXLY_` prefix):

!!! code "Run via Environment Variables"
    ```bash
    export FLUXLY_MESSAGE="hello"
    python main.py my-workflow
    ```

---

## Generated Entrypoints (CLI and API)

Fluxly auto-generates a CLI menu and API routes per registered workflow.

!!! note "CLI Menu"
    <div align="center">
      <img src="imgs/cli_menu.png" alt="Fluxly CLI Menu" title="Fluxly CLI Menu" style="max-width: 700px; width: 100%;" />
      <p><em>CLI commands generated for your workflows.</em></p>
    </div>

!!! note "Swagger UI"
    <div align="center">
      <img src="imgs/swagger.png" alt="Fluxly Swagger UI" title="Fluxly Swagger UI" style="max-width: 700px; width: 100%;" />
      <p><em>API endpoints for submitting runs and fetching statuses.</em></p>
    </div>

---

## Where to go next

- Getting started: project layout, environment, and running the included demo — [Getting started](getting-started.md)  
- Core concepts: workflows, nodes, execution groups, orchestration controls, and node-to-node communication — [Core concepts](concepts.md)  
