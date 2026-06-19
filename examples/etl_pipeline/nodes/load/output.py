from typing import Annotated

from pydantic import Field

from fluxly.node import NodeOutput


class LoadOutput(NodeOutput):
    loaded_count: Annotated[int, Field(description="Number of records written to the destination")] = 0
