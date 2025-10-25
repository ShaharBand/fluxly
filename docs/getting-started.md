# Getting Started with Fluxly

Fluxly lets you **quickly design, run, and manage DAG-based workflows**.  
Workflows can be triggered via **CLI, API, or environment variables**, so the same workflow works in any context.  
This guide walks you through creating your first workflow, adding nodes, handling inputs, and executing it through your chosen entrypoint.

---

## 1. Install Fluxly

Install via pip:

!!! code "Install via pip"
    ```bash
    pip install fluxly
    ```

Or clone the repository for development:

!!! code "Clone for development"
    ```bash
    git clone https://github.com/ShaharBand/fluxly.git
    cd fluxly
    pip install -e .
    ```

---

## 2. Define a Workflow Input

Workflows use **typed inputs** with Pydantic for validation.  
These inputs can be provided via **CLI flags, API payloads, or environment variables**, keeping your workflows flexible and consistent.  
Annotate fields with descriptions and constraints to improve validation and automatically generate help text for any entrypoint.

!!! code "Workflow Input Example"
    ```python
    from typing import Annotated

    from pydantic import Field
    from fluxly.workflow import WorkflowInput

    class MyWorkflowInput(WorkflowInput):
        message: Annotated[str, Field(min_length=1, max_length=100, description="Message to print")] = "Hello, Fluxly!"
        repeat: Annotated[int, Field(ge=1, le=10, description="How many times to repeat")] = 3
    ```

---

## 3. Create Nodes

Nodes encapsulate **single units of work**. Each node receives the workflow input and communicates results via **typed outputs**, avoiding ad-hoc dictionaries or positional references.

!!! code "Node Example"
    ```python
    from fluxly.node import Node

    class PrintNode(Node):
        @property
        def workflow_input(self) -> MyWorkflowInput:
            return self._workflow_input

        def _logic(self) -> None:
            for i in range(self.workflow_input.repeat):
                self._logger.info(f"{i+1}: {self.workflow_input.message}")
    ```

---

## 4. Assemble a Workflow

Create a workflow, add nodes, and define their dependencies.

!!! code "Assemble Workflow"
    ```python
    from fluxly.workflow import Workflow

    workflow = Workflow(name="demo-workflow")

    # Nodes
    node_a = PrintNode(name="PrintMessage")

    # Add nodes
    workflow.add_node(node_a)

    # Optionally, add edges if multiple nodes exist
    # workflow.add_edge(node_a, node_b)
    # workflow.add_edge_if_source_completed(node_a, node_b)  # run node_b only if node_a completed
    ```

---

## 5. Execute the Workflow

Fluxly exposes your workflow as a **entrypoint** that can be triggered via **CLI, API, or environment variables**.  
Your `WorkflowInput` is the single source of truth for both **CLI flags** and **API payload** validation.

!!! code "Execute Workflow"
    ```python
    from fluxly import Fluxly

    app = Fluxly()
    app.add_endpoint("run-demo", workflow, MyWorkflowInput)
    app.run()  # auto: CLI if args present, otherwise API server
    ```

Run from the terminal (CLI example):

!!! code "Run CLI"
    ```bash
    python your_script.py run-demo --message "Hi there!" --repeat 5
    ```

Trigger via **HTTP POST request**:

!!! code "Run via API"
    ```python
    import requests

    url = "http://localhost:8000/run-demo/run"
    payload = {"message": "Hello!"}

    response = requests.post(url, json=payload)
    print(response.status_code, response.json())
    ```

Trigger via **environment variables** (with `FLUXLY_` prefix to avoid collisions):

!!! code "Run via Environment Variables"
    ```bash
    export FLUXLY_MESSAGE="Hello!"
    export FLUXLY_REPEAT=5
    python your_script.py run-demo
    ```

### Choose your entrypoint explicitly

Use one of the following based on your deployment context:

- `app.run()` — auto-selects: runs CLI when arguments are provided, otherwise starts the API server.
- `app.run_cli()` — force CLI mode.
- `app.run_api()` — force API server.

!!! code "Explicit run modes"
    ```python
    from fluxly import Fluxly

    app = Fluxly()
    app.add_endpoint("run-demo", workflow, MyWorkflowInput)

    # Force CLI
    # app.run_cli()

    # Force API
    # app.run_api()
    ```

### Configure the FastAPI/Uvicorn server

You can pass FastAPI and Uvicorn settings via `ApiConfig` and `app.configure_api()`.

!!! code "API configuration"
    ```python
    from fluxly import Fluxly
    from fluxly.api.server import ApiConfig

    app = Fluxly()
    app.add_endpoint("run-demo", workflow, MyWorkflowInput)

    app.configure_api(
        ApiConfig(
            host="0.0.0.0",
            port=9000,
            log_level="info",
            fastapi_kwargs={
                "docs_url": "/docs",
                "openapi_url": "/openapi.json",
            },
            uvicorn_kwargs={
                "reload": True,
                # any other uvicorn.run kwargs
            },
        )
    )

    app.run_api()
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
        def on_start(self) -> None:
            self._logger.info(f"Starting node: {self.name}")

        def on_success(self) -> None:
            self._logger.info(f"Finished node: {self.name}")

        def on_failure(self, error) -> None:
            self._logger.info(f"Node {self.name} failed: {error}")
    ```

---

## 7. Enable Auto-Generated Documentation
 
 Fluxly can automatically generate **Markdown documentation** and **DAG diagrams**.  
You can configure this either:

- **Programmatically**: set defaults in `workflow.inputs`.
- **At runtime**: provide flags, API payloads, or environment variables; all map to `WorkflowInput` fields.

!!! code "Programmatic defaults (set once)"
    ```python
    # Set default documentation behavior on the workflow template
    workflow.inputs = MyWorkflowInput(
        auto_generate_md=True,
        md_file_path="workflow_doc.md",
        diagram_file_path="workflow_diagram.png",
    )
    ```

Run from the terminal (CLI example):

!!! code "Override via CLI flags"
    ```bash
    python your_script.py run-demo \
      --auto-generate-md \
      --md-file-path workflow_doc.md \
      --diagram-file-path workflow_diagram.png
    ```

Trigger via **API POST request**:

!!! code "Override via API"
    ```python
    import requests

    url = "http://localhost:8000/run-demo/run"
    payload = {
        "auto_generate_md": True,
        "md_file_path": "workflow_doc.md",
        "diagram_file_path": "workflow_diagram.png",
    }

    response = requests.post(url, json=payload)
    print(response.status_code, response.json())
    ```

Trigger via **environment variables** (with `FLUXLY_` prefix):

!!! code "Override via Environment Variables"
    ```bash
    export FLUXLY_AUTO_GENERATE_MD=1
    export FLUXLY_MD_FILE_PATH="workflow_doc.md"
    export FLUXLY_DIAGRAM_FILE_PATH="workflow_diagram.png"
    python your_script.py run-demo
    ```

!!! note
    At the end of execution, Fluxly outputs a **readable summary** and a **diagram** of the workflow.  
    This is useful for **reviews, knowledge sharing, and onboarding new developers**.

---

## 8. Next Steps

- Add **conditional edges** and **parallel execution groups**.
- Explore **typed exceptions** for reliable error handling.
- Integrate with **logging, metrics, or CI/CD pipelines**.
- Write **unit tests** for workflows and nodes to ensure predictable behavior.

!!! note
    Once you are comfortable with the basics, you can start building **production-ready pipelines** using Fluxly, scaling from **local scripts to distributed workflows**.
