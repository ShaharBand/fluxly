from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from fluxly.core.workflow.execution import WorkflowExecution


class ApiConfig(BaseModel):
    host: str = "127.0.0.1"
    port: int = 8000
    log_level: str = "info"
    fastapi_kwargs: dict[str, Any] = {}
    uvicorn_kwargs: dict[str, Any] = {}


class RunRecord(BaseModel):
    run_id: str | None = None
    endpoint: str
    workflow_name: str | None = None
    workflow_version: str | None = None
    workflow_id: str | None = None
    status: str | None = None
    submitted_at: str
    started_at: str | None = None
    executions: list[WorkflowExecution] | None = None
    error: str | None = None
