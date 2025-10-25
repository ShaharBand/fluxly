from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from fluxly.core.api.handlers import (
    EndpointRunner,
    get_run_by_endpoint_handler,
    get_run_handler,
    health_handler,
)
from fluxly.core.api.models import ApiConfig
from fluxly.core.api.service import RunnerService
from fluxly.core.utils.consts import PACKAGE_VERSION
from fluxly.core.workflow.input import WorkflowInput
from fluxly.core.workflow.workflow import Workflow


def build_app(endpoints: dict[str, tuple[Workflow, type[WorkflowInput]]], config: ApiConfig) -> FastAPI:
    app = FastAPI(title="Fluxly API", version=PACKAGE_VERSION, **config.fastapi_kwargs)
    service = RunnerService()

    for endpoint_name, (workflow_template, wf_input_cls) in endpoints.items():
        runner = EndpointRunner(name=endpoint_name, workflow=workflow_template, input_cls=wf_input_cls, service=service)
        route_summary = f"Submit {endpoint_name} workflow run"
        route_description = (
            f"Workflow: {workflow_template.name}\n\n"
            f"Version: {workflow_template.version or 'N/A'}\n\n"
            f"Description: {workflow_template.description or ''}"
        )
        app.add_api_route(
            f"/{endpoint_name}/run",
            runner.submit,
            methods=["POST"],
            name=f"{endpoint_name}-run",
            summary=route_summary,
            description=route_description,
            tags=[endpoint_name],
            openapi_extra={
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": wf_input_cls.model_json_schema()
                        }
                    },
                }
            },
        )

    app.get("/runs/{run_id}")(get_run_handler(service))
    app.get("/{endpoint}/runs/{run_id}")(get_run_by_endpoint_handler(service))
    app.get("/health")(health_handler)

    return app


def serve(endpoints: dict[str, tuple[Workflow, type[WorkflowInput]]], config: ApiConfig) -> None:
    app = build_app(endpoints, config)
    uvicorn.run(app, host=config.host, port=config.port, log_level=config.log_level, **config.uvicorn_kwargs)


