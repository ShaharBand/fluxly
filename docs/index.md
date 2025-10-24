<div align="center">
  <img src="imgs/logo.jpg" alt="FluxCLI Logo" title="FluxCLI Logo" style="max-width: 200px;" />
  
  <h1>FluxCLI</h1>
  <p><em>Lightweight, CLI-first framework for building <strong>DAG-based workflows</strong></em></p>

  <p>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.10%2B-blue.svg" alt="Python 3.10+"></a>
    <a href="https://github.com/ShaharBand/fluxcli"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License MIT"></a>
  </p>
</div>

---

FluxCLI lets you build and run structured, DAG-based workflows where each workflow becomes a **CLI command**. It's **local-first** for easy debugging and **portable** for orchestration.

---

!!! note "Complex workflow"
    <div align="center">
      <img src="imgs/complex_workflow.png" alt="Complex Workflow Diagram" title="Complex Workflow Diagram" style="max-width: 700px; width: 100%;" />
      <p><em>Branching, conditional edges, and parallel paths stay readable.</em></p>
    </div>

---

## Key Features

- CLI-based workflow with **typed inputs/outputs**
- DAG-based workflow orchestration with **validation, retries, and isolation**
- Strong isolation between nodes with explicit data flow
- Extensible **lifecycle hooks** and custom exceptions with exit codes
- Auto-generated **docs and diagrams**

---

## Installation

!!! code "Install FluxCLI"
    ```bash
    pip install fluxcli
    ```

---

## Quick Start

### 1) Define inputs and a node

Create a typed `WorkflowInput` (validated by Pydantic) and a `Node` containing your main logic in `_logic()`.  
Each node receives a strongly-typed `workflow_input`, keeping your code safe and easy to read.

!!! code "Node & Input Example"
    ```python
    from fluxcli.node import Node
    from fluxcli.workflow import Workflow, WorkflowInput

    class MyInput(WorkflowInput):
        message: str = "world"

    class Echo(Node):
        _workflow_input: MyInput

        @property
        def workflow_input(self) -> MyInput:
            return self._workflow_input

        def _logic(self) -> None:
            print(f"Echo: {self.workflow_input.message}")
    ```

### 2) Build a workflow

Create a `Workflow`, add nodes to it, and wire edges/conditions to express execution order and data dependencies.  
Workflows orchestrate retries, timeouts, and overall execution.

!!! code "Workflow Example"
    ```python
    def build_workflow() -> Workflow:
        wf = Workflow(name="demo", description="Demo flow", version="0.1")

        # Define nodes
        alpha = Echo(name="alpha", description="prints a message", timeout_seconds=5)
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

### 3) Wire into a CLI

Use `FluxCLI` to expose your workflow as a single command. CLI flags are auto-generated from your `WorkflowInput` fields (with types and defaults), so your interface stays consistent with your code.

!!! code "Expose Workflow via CLI"
    ```python
    from fluxcli import FluxCLI

    if __name__ == "__main__":
        cli = FluxCLI()
        # Register command name, workflow class/factory, and input model
        cli.add_command("my-workflow", build_workflow, MyInput)
        cli.run()
    ```

Run it:

!!! code "Run the CLI"
    ```bash
    python cli.py my-workflow --message hello

    # discover generated flags and help text
    python cli.py my-workflow --help
    ```

---

## Where to go next

- Getting started: project layout, environment, and running the included demo — [Getting started](getting-started.md)  
- Core concepts: workflows, nodes, execution groups, orchestration controls, and node-to-node communication — [Core concepts](concepts.md)  
