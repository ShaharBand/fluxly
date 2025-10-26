<div align="center">
  <img src="./docs/imgs/logo.png" 
       style="max-width: 250px;" 
       alt="Fluxly Logo" 
       title="Fluxly Logo">


![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)

Fluxly — Lightweight framework for portable, self-contained DAG workflows, decoupled from orchestration.

</div>

---

**Fluxly** is a lightweight framework for building and running **directed acyclic graph (DAG)-based workflows**.  

The entire workflow acts as a **self-contained execution endpoint**:

- Run them locally or via CLI commands, API calls, or environment triggers.
- Package them in containers for portability.
- Integrate seamlessly with higher-level orchestrators (Argo, Airflow, Prefect, CI/CD) without extra glue code.

With **Fluxly**, pipelines are **highly structured**, enabling safer execution, easier debugging, and better modularity.  
Workflows can run standalone or as part of a larger system, making **Fluxly** both lightweight and flexible.

## Why Fluxly (the problem it solves)

- Unstructured container pipelines tend to become spaghetti: ad‑hoc scripts across containers, inconsistent inputs/outputs, and scattered retries/timeouts/logging with no shared wrapper.
- Heavyweight orchestrators like Airflow add operational burden (schedulers, DBs, webservers, DAG deployment) when all you need is a simple, portable workflow image.
- Orchestrator‑coupled SDKs (e.g., Prefect) optimize for remote control planes and persistent backends, introducing communication channels and runtime coupling that don’t fit autonomous, fire‑and‑forget jobs.
- Fluxly keeps logic structured and isolated inside a single codebase and container: typed I/O models, explicit DAG, uniform entrypoints (CLI/API/env), and clear node boundaries. Any scheduler can trigger it, but your workflow remains clean and portable.
- Best when each Docker stays simple and self‑sufficient, and you want clarity, low overhead, and no hidden glue.
- In monorepos—or by wrapping Fluxly—you can centralize shared services, typed inputs, validations, outputs, and metadata to fit your org standards. This thin wrapper standardizes containers and removes boilerplate across pipelines.

---

<img src="docs/imgs/complex_workflow.png" alt="Complex Workflow Diagram" title="Complex Workflow Diagram" style="max-width: 700px; width: 100%;" />

---

## Generated Entrypoints (CLI and API)

The package automatically exposes a CLI command and API endpoints for each registered workflow.

<div align="center">
  <img src="docs/imgs/cli_menu.png" alt="Fluxly CLI Menu" title="Fluxly CLI Menu" style="max-width: 700px; width: 100%;" />
  <p><em>Auto-generated CLI commands per workflow.</em></p>
</div>

<div align="center">
  <img src="docs/imgs/swagger.png" alt="Fluxly Swagger UI" title="Fluxly Swagger UI" style="max-width: 700px; width: 100%;" />
  <p><em>Auto-generated API endpoints per workflow in Swagger UI.</em></p>
</div>

---

## Documentation

Comprehensive documentation for Fluxly is available online:

- **View the docs:** [GitHub Pages](https://shaharband.github.io/fluxly/)

---

## 1. Key Features

- **Flexible entrypoints** – workflows can be triggered via CLI, API calls, or environment variables.
- **DAG-based workflows** – define arbitrary connections between nodes and their dependencies.
- **Highly structured workflows** – strict validation ensures safer pipelines, easier debugging, and predictable behavior.
- **Self-orchestrated nodes** – each node manages its own execution, retries, and dependencies.
- **Lightweight building blocks** – workflows are self-contained units that can run independently in any environment.
- **Extensible by design** – wrap workflows with custom classes to add logging, metrics, or integrations.
- **Local-first development** – debug and run workflows standalone, then scale seamlessly to CI/CD or external orchestrators.

---

## 2. Technology Stack

- [**Pydantic**](https://github.com/pydantic/pydantic): Strict data validation and schema for inputs/outputs.
- [**Typer**](https://github.com/fastapi/typer): Easy wrapper for building great CLIs.
- [**FastAPI**](https://github.com/tiangolo/fastapi): Modern, high-performance web framework for building APIs.  
- [**Uvicorn**](https://www.uvicorn.org/): Lightning-fast ASGI server for running FastAPI apps. 
- [**Loguru**](https://github.com/Delgan/loguru): Simple, efficient logging for Python.
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
pip install fluxly
```
