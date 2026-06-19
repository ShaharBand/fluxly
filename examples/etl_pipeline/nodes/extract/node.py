import json
from pathlib import Path

import requests
from pydantic import ValidationError

from examples.etl_pipeline.nodes.extract.execution import ExtractExecution
from examples.etl_pipeline.nodes.extract.output import UserRecord
from examples.etl_pipeline.workflow.input import EtlInput
from fluxly.exceptions import DataErrorException, NetworkFailureException
from fluxly.node import Node


class Extract(Node):
    _workflow_input: EtlInput

    @property
    def current_execution(self) -> ExtractExecution:
        return super().current_execution

    @property
    def last_execution(self) -> ExtractExecution:
        return super().last_execution

    @property
    def workflow_input(self) -> EtlInput:
        return self._workflow_input

    def _create_execution(self) -> ExtractExecution:
        return ExtractExecution()

    def _load_payload(self) -> list[dict[str, object]]:
        source = self.workflow_input.source_url
        source_path = Path(source)
        if source_path.is_file():
            return json.loads(source_path.read_text(encoding="utf-8"))

        try:
            response = requests.get(source, timeout=10)
            response.raise_for_status()
        except requests.RequestException as error:
            raise NetworkFailureException(f"Could not reach source: {error}") from error

        payload = response.json()
        if not isinstance(payload, list):
            raise DataErrorException("Source must return a JSON array of user records")
        return payload

    def _logic(self) -> None:
        try:
            rows = self._load_payload()
            self.current_execution.output.records = [UserRecord.model_validate(row) for row in rows]
        except ValidationError as error:
            raise DataErrorException(f"Source returned malformed records: {error}") from error

        self._logger.info(f"Extracted {len(self.current_execution.output.records)} records")
