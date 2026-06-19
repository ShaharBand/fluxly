from examples.etl_pipeline.nodes.extract.node import Extract
from examples.etl_pipeline.nodes.extract.output import UserRecord
from examples.etl_pipeline.nodes.transform.execution import TransformExecution
from examples.etl_pipeline.workflow.input import EtlInput
from fluxly.node import Node


class Transform(Node):
    _workflow_input: EtlInput
    extract: Extract

    @property
    def current_execution(self) -> TransformExecution:
        return super().current_execution

    @property
    def last_execution(self) -> TransformExecution:
        return super().last_execution

    @property
    def workflow_input(self) -> EtlInput:
        return self._workflow_input

    def _create_execution(self) -> TransformExecution:
        return TransformExecution()

    def _logic(self) -> None:
        records = self.extract.last_execution.output.records
        clean: list[UserRecord] = []
        dropped = 0

        for record in records:
            email = record.email.strip().lower()
            if "@" not in email:
                dropped += 1
                continue
            clean.append(UserRecord(userId=record.user_id, email=email))

        self.current_execution.output.clean_records = clean
        self.current_execution.output.dropped_count = dropped
        self._logger.info(
            f"Normalized {len(clean)} records ({dropped} dropped)",
        )
