from typing import Annotated

from pydantic import Field

from examples.etl_pipeline.nodes.extract.output import UserRecord
from fluxly.node import NodeOutput


class TransformOutput(NodeOutput):
    clean_records: Annotated[
        list[UserRecord],
        Field(description="Normalized user records ready for loading"),
    ] = []
    dropped_count: Annotated[int, Field(description="Records dropped during normalization")] = 0
