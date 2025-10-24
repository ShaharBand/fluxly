<div align="center">
  <img src="./docs/imgs/logo.jpg" 
       style="max-width: 250px;" 
       alt="FluxCLI Logo" 
       title="FluxCLI Logo">


![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)

FluxCLI - Lightweight, CLI-first framework for building **directed acyclic graph (DAG)**-based workflows.

</div>

---

FluxCLI is a lightweight framework for building and running **DAG-based workflows**.  
Each workflow is defined as a **graph of command-line actions**, and the entire graph itself becomes a **single CLI command**.

This design makes workflows fully **self-contained**:

- Run them locally as normal CLI tools.
- Wrap them in Docker images for portability.
- Plug them into higher-level orchestrators (Argo, Airflow, Prefect, CI/CD) without extra glue code.

With FluxCLI, pipelines are **highly structured** for safer execution, cleaner debugging, and better modularity.  
Workflows can run standalone or as part of a larger system, making FluxCLI both lightweight and flexible.

---

<img src="docs/imgs/complex_workflow.png" alt="Complex Workflow Diagram" title="Complex Workflow Diagram" style="max-width: 700px; width: 100%;" />

---

## Documentation

Full documentation is hosted on GitHub Pages:

- Hosted docs: https://shaharband.github.io/fluxcli/


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
- [**MkDocs**](https://github.com/mkdocs/mkdocs/): Documentation generator for Markdown-based docs.
- [**Material for MkDocs**](https://github.com/squidfunk/mkdocs-material): Modern, responsive theme for MkDocs.
- **GitHub CI/CD**: Continuous integration and deployment.

---

## 3. Installation

Install with `pip`:

```bash
pip install fluxcli
```

---
