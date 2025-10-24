## WorkflowInput Flags for CLI and Documentation

Fields in a `WorkflowInput` are used to **auto-generate CLI flags** and **documentation**.  
You can control how each field is exposed or presented using `json_schema_extra`.

!!! note "Supported Extras per Field"
    - `exclude_from_cli`: if `True`, the field is **omitted from the CLI**.  
    - `convert_underscores`: if `False`, field name underscores are preserved (default converts underscores to dashes).  
    - `exclude_from_documentation`: if `True`, the field is **omitted from generated docs**.

!!! code "WorkflowInput Example"
    ```python
    from typing import Annotated
    from pydantic import Field
    from fluxcli.workflow import WorkflowInput

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
