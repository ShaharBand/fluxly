from typing import Annotated

from pydantic import BaseModel, Field


class WorkflowInput(BaseModel):
    cli_command_name: Annotated[str | None, Field(None, description="CLI command name for the workflow.", json_schema_extra={'exclude_from_cli': 'True'})]
    verbose: Annotated[bool, Field(description="Print more details for debug")] = True
    timeout_seconds: Annotated[int | None, Field(default=None, gt=0, description="Timeout for the workflow in seconds.")] = None
    max_retries: Annotated[int, Field(ge=0, description="Maximum number of run attempts allowed in case of failure.")] = 0
    retry_delay_seconds: Annotated[int, Field(ge=0, description="Delay between retries in seconds.")] = 0
    auto_generate_md: Annotated[bool, Field(description="Automatically generate markdown file for the workflow input documentation")] = False
    md_file_path: Annotated[str, Field(description="Path to save the generated markdown file.")] = "workflow_documentation.md"
    diagram_file_path: Annotated[str, Field(description="Path to save the generated workflow graph diagram image (png).")] = "workflow_diagram.png"
    # Annotated[int, Field(description="Something.",
    # json_schema_extra={
    #   'exclude_from_cli': 'True',
    #   'convert_underscores': False,
    #   'exclude_from_documentation': False
    # })]
