## WorkflowInput schema for CLI flags and API payloads

`WorkflowInput` is the single source of truth for your workflow’s inputs.  
Its fields are used to both **auto-generate CLI flags** and **validate API payloads**, and also power generated documentation.  
You can control how each field is exposed or presented using `json_schema_extra`.

!!! note "Supported Extras per Field"
    - `exclude_from_cli`: if `True`, the field is **omitted from the CLI**.  
    - `convert_underscores`: if `False`, field name underscores are preserved (default converts underscores to dashes).  
    - `exclude_from_documentation`: if `True`, the field is **omitted from generated docs**.

!!! note
    These options affect CLI flag generation and docs. API payload validation still follows the `WorkflowInput` schema.

!!! code "WorkflowInput Example"
    ```python
    from typing import Annotated
    
    from pydantic import Field
    from fluxly.workflow import WorkflowInput

    class MyInput(WorkflowInput):
        secret_token: Annotated[str | None, Field(
            default=None,
            description="Authentication token",
            json_schema_extra={"exclude_from_cli": True, "exclude_from_documentation": True},
        )]

        cool_flag: Annotated[bool, Field(
            default=False,
            description="Enable cool stuff",
            json_schema_extra={"convert_underscores": True},
        )]
    ```
