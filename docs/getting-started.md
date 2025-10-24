# Getting Started with FluxCLI

FluxCLI lets you **quickly design, run, and manage DAG-based workflows** using **Python and CLI commands**.  
This guide walks you through creating your first workflow, adding nodes, handling inputs, and executing it via the CLI.

---

## 1. Install FluxCLI

Install via pip:

!!! code "Install via pip"
    ```bash
    pip install fluxcli
    ```

Or clone the repository for development:

!!! code "Clone for development"
    ```bash
    git clone https://github.com/your-repo/fluxcli.git
    cd fluxcli
    pip install -e .
    ```

---

## 2. Define a Workflow Input

Workflows use **typed inputs** with Pydantic for validation.  
This allows your CLI commands to be auto-generated with **type hints, defaults, and descriptions**.

!!! code "Workflow Input Example"
    ```python
    from fluxcli.workflow import WorkflowInput

    class MyWorkflowInput(WorkflowInput):
        message: str = "Hello, FluxCLI!"
        repeat: int = 3
    ```

---

## 3. Create Nodes

Nodes encapsulate **single units of work**. Each node receives the workflow input and communicates results via **typed outputs**, avoiding ad-hoc dictionaries or positional references.

!!! code "Node Example"
    ```python
    from fluxcli.node import Node

    class PrintNode(Node):
        _workflow_input: MyWorkflowInput

        def _logic(self):
            for i in range(self._workflow_input.repeat):
                print(f"{i+1}: {self._workflow_input.message}")
    ```

---

## 4. Assemble a Workflow

Create a workflow, add nodes, and define their dependencies.

!!! code "Assemble Workflow"
    ```python
    from fluxcli.workflow import Workflow

    workflow = Workflow(name="demo-workflow")

    # Nodes
    node_a = PrintNode(name="PrintMessage")

    # Add nodes
    workflow.add_node(node_a)

    # Optionally, add edges if multiple nodes exist
    # workflow.add_edge(node_a, node_b)
    ```

---

## 5. Execute the Workflow via CLI

FluxCLI automatically generates CLI commands based on your workflow and input class.

!!! code "CLI Execution"
    ```python
    from fluxcli import FluxCLI

    cli = FluxCLI()
    cli.add_command("run-demo", lambda: workflow, MyWorkflowInput)
    cli.run()
    ```

Run from terminal:

!!! code "Run from terminal"
    ```bash
    python your_script.py run-demo --message "Hi there!" --repeat 5
    ```

---

## 6. Handle Lifecycle Hooks

Extend nodes with **hooks** for logging, metrics, cleanup, or notifications. Hooks exist for both nodes and workflows:

- `on_start` – before execution  
- `on_success` – after successful completion  
- `on_failure` – after failure  
- `on_finish` – always called

!!! code "Lifecycle Hooks Example"
    ```python
    class LoggingNode(PrintNode):
        def on_start(self):
            print(f"Starting node: {self.name}")

        def on_success(self):
            print(f"Finished node: {self.name}")

        def on_failure(self, error):
            print(f"Node {self.name} failed: {error}")
    ```

---

## 7. Enable Auto-Generated Documentation

FluxCLI can automatically generate **Markdown documentation** and **DAG diagrams** for your workflows.

!!! code "Auto Documentation"
    ```python
    workflow.inputs.auto_generate_md = True
    workflow.inputs.md_file_path = "workflow_doc.md"
    workflow.inputs.diagram_file_path = "workflow_diagram.png"
    ```

!!! note
    At the end of execution, FluxCLI outputs a **readable summary** and a **diagram** of the workflow.  
    Useful for **reviews, knowledge sharing, and onboarding new developers**.

---

## 8. Next Steps

- Add **conditional edges** and **parallel execution groups**.
- Explore **typed exceptions** for reliable error handling.
- Integrate with **logging, metrics, or CI/CD pipelines**.
- Write **unit tests** for workflows and nodes to ensure predictable behavior.

!!! note
    Once you are comfortable with the basics, you can start building **production-ready pipelines** using FluxCLI, scaling from **local scripts to distributed workflows**.
