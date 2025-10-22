from typing import Annotated

from pydantic import Field

from flowcli.node import NodeOutput


class BetaOutput(NodeOutput):
    combined: Annotated[str, Field(description="Output combined message")] = ""
