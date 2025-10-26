from __future__ import annotations

import copy
import threading
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fluxly.core.api.models import RunRecord
from fluxly.core.status import StatusCodes
from fluxly.core.workflow.input import WorkflowInput
from fluxly.core.workflow.models import EndpointType
from fluxly.core.workflow.workflow import Workflow


class RunnerService:
    def __init__(self) -> None:
        self._runs: dict[str, RunRecord] = {}

    def submit(self, endpoint: str, workflow: Workflow, input_cls: type[WorkflowInput], values: dict[str, Any]) -> RunRecord:
        wf = copy.deepcopy(workflow)
        wf.inputs = input_cls(**values)

        run_id = wf.run_id or str(uuid4())
        wf.assign_run_id(run_id)
        wf.assign_trigger(endpoint_type=EndpointType.API, endpoint_name=endpoint)
        record = RunRecord(
            run_id=run_id,
            endpoint=endpoint,
            workflow_name=wf.name,
            workflow_version=wf.version,
            submitted_at=datetime.now(UTC).isoformat(),
            status=StatusCodes.WAITING.name,
        )
        self._runs[run_id] = record

        def _run() -> None:
            rec = self._runs[run_id]
            rec.status = StatusCodes.IN_PROGRESS.name
            rec.started_at = datetime.now(UTC).isoformat()
            rec.workflow_id = wf.id
            try:
                wf.execute()
                latest = wf.last_execution
                rec.status = latest.status.name
                rec.executions = wf.executions
            except Exception as e:
                latest = wf.last_execution
                rec.status = latest.status.name if latest else StatusCodes.FAILED.name
                rec.executions = wf.executions
                rec.error = str(e)

        threading.Thread(target=_run, daemon=True).start()
        return record

    def get(self, run_id: str) -> RunRecord | None:
        return self._runs.get(run_id)


