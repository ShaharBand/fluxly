from typing import Annotated

from pydantic import Field

from fluxly.core.node import NodeOutput


class AlphaNodeOutput(NodeOutput):
    echoed: Annotated[str, Field(description="Echoed message from Alpha")] = ""
