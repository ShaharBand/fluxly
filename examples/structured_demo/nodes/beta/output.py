from typing import Annotated

from pydantic import Field

from fluxly.node import NodeOutput


class BetaOutput(NodeOutput):
    combined: Annotated[str, Field(description="Output combined message")] = ""
