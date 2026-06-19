from typing import Annotated

from pydantic import Field

from fluxly.workflow import WorkflowInput


class EtlInput(WorkflowInput):
    source_url: Annotated[
        str,
        Field(description="API endpoint or local JSON file path to extract user records from"),
    ] = "examples/etl_pipeline/fixtures/users.json"
    batch_size: Annotated[int, Field(gt=0, description="Rows to load per batch")] = 500
    dry_run: Annotated[bool, Field(description="Skip the final write when True")] = False
