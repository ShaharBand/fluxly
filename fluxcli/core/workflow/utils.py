from fluxcli.core.workflow.input import WorkflowInput


def build_cli_command_from_workflow_input(workflow_input: WorkflowInput) -> str:
    flags = []
    for field_name, field in workflow_input.__pydantic_fields__.items():
        if field.json_schema_extra and field.json_schema_extra.get("exclude_from_cli"):
            continue

        value = getattr(workflow_input, field_name)
        default = field.default if field.default is not None else None

        if value is None or (isinstance(value, str) and not value.strip()) or str(value) == str(default):
            continue

        flag = f"--{field_name.replace('_', '-')}"
        if isinstance(value, bool):
            flags.append(flag if value else f"--no-{field_name.replace('_', '-')}")
        elif isinstance(value, list):
            for item in value:
                flags.append(f"{flag} {item}")
        else:
            flags.append(f"{flag} {value}")

    command_name = workflow_input.cli_command_name
    return f"{command_name} {' '.join(flags)}"
