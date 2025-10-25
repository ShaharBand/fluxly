# Structured Demo

Fluxly includes a **structured demo** showcasing how to register and run workflows through the framework.

!!! note "Entry Point"
    Located at: `examples/structured_demo/app.py`

Run the demo from the terminal (CLI):

!!! code
    ```bash
    python examples/structured_demo/app.py structured-demo [--flags]
    ```

Trigger the workflow via an **HTTP POST request**:

!!! code "API POST Example"
    ```python
    import requests

    url = "http://localhost:8000/structured-demo/run"
    payload = {"message": "Hello, structured demo!"}

    response = requests.post(url, json=payload)
    print(response.status_code, response.json())
    ```

Or trigger it via **environment variables** (with `FLUXLY_` prefix to avoid collisions):

!!! code "Environment Variables Example"
    ```bash
    export FLUXLY_MESSAGE="Hello, structured demo!"
    python examples/structured_demo/app.py structured-demo
    ```

This example demonstrates how **workflows, nodes, and typed inputs** integrate under the framework, whether run via **CLI, API, or environment variables**.
