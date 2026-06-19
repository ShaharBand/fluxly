from examples.etl_pipeline.nodes.load.execution import LoadExecution
from examples.etl_pipeline.nodes.transform.node import Transform
from examples.etl_pipeline.workflow.input import EtlInput
from fluxly.node import Node


class Load(Node):
    _workflow_input: EtlInput
    transform: Transform

    @property
    def current_execution(self) -> LoadExecution:
        return super().current_execution

    @property
    def last_execution(self) -> LoadExecution:
        return super().last_execution

    @property
    def workflow_input(self) -> EtlInput:
        return self._workflow_input

    def _create_execution(self) -> LoadExecution:
        return LoadExecution()

    def _logic(self) -> None:
        records = self.transform.last_execution.output.clean_records
        batch_size = self.workflow_input.batch_size

        if self.workflow_input.dry_run:
            self.current_execution.output.loaded_count = len(records)
            self._logger.info(
                f"Would load {len(records)} rows in batches of {batch_size}",
            )
            return

        loaded = 0
        for start in range(0, len(records), batch_size):
            batch = records[start : start + batch_size]
            loaded += len(batch)

        self.current_execution.output.loaded_count = loaded
        self._logger.info(f"Loaded {loaded} rows")
