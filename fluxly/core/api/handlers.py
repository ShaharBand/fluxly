from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ValidationError

from fluxly.core.api.service import RunnerService
from fluxly.core.workflow.input import WorkflowInput
from fluxly.core.workflow.workflow import Workflow


class EndpointRunner(BaseModel):
    model_config = {"arbitrary_types_allowed": True}
    name: str
    workflow: Workflow
    input_cls: type[WorkflowInput]
    service: RunnerService

    async def submit(self, payload: dict[str, Any]) -> JSONResponse:
        values = payload
        try:
            self.input_cls(**values)
        except (ValidationError) as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(e))

        record = self.service.submit(self.name, self.workflow, self.input_cls, values)
        return JSONResponse(status_code=status.HTTP_202_ACCEPTED, content=record.model_dump())


def get_run_handler(service: RunnerService):
    async def _get_run(run_id: str) -> Any:
        record = service.get(run_id)
        if not record:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
        return record.model_dump()

    return _get_run


def get_run_by_endpoint_handler(service: RunnerService):
    async def _get_run_by_endpoint(endpoint: str, run_id: str) -> Any:
        record = service.get(run_id)
        if not record or record.endpoint != endpoint:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
        return record.model_dump()

    return _get_run_by_endpoint


async def health_handler() -> dict[str, str]:
    return {"status": "ok"}


