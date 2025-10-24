from typing import Annotated

from pydantic import Field

from fluxcli.core.workflow.input import WorkflowInput as CoreWorkflowInput


class DemoWorkflowInput(CoreWorkflowInput):
    message: Annotated[str | None, Field(description="Optional message passed to Alpha")] = None
    suffix: Annotated[str | None, Field(description="Optional suffix passed to Beta")] = None



