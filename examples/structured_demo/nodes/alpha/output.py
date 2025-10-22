from typing import Annotated

from pydantic import Field

from flowcli.core.node import NodeOutput


class AlphaNodeOutput(NodeOutput):
    echoed: Annotated[str, Field(description="Echoed message from Alpha")] = ""
