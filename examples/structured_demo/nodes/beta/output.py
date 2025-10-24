from typing import Annotated

from pydantic import Field

from fluxcli.node import NodeOutput


class BetaOutput(NodeOutput):
    combined: Annotated[str, Field(description="Output combined message")] = ""
