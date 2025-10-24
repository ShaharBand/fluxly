import copy
from typing import Any

import click
from pydantic import ValidationError

from fluxcli.core.workflow.input import WorkflowInput
from fluxcli.core.workflow.workflow import Workflow


def _json_type_to_click_type(json_type: str) -> Any:
    mapping: dict[str, Any] = {"integer": int, "number": float, "string": str}
    return mapping.get(json_type, str)


def _resolve_field_type(meta: dict[str, Any] | None) -> str:
    if not meta:
        return "string"
    t = meta.get("type")
    if t:
        return t
    any_of = meta.get("anyOf") or meta.get("oneOf") or []
    for variant in any_of if isinstance(any_of, list) else []:
        if isinstance(variant, dict) and variant.get("type") and variant.get("type") != "null":
            return variant.get("type")  # type: ignore[return-value]
    return "string"


def _get_properties_and_required(workflow_input_cls: type[WorkflowInput]) -> tuple[dict[str, Any], set[str]]:
    schema: dict[str, Any] = workflow_input_cls.model_json_schema()
    return schema.get("properties", {}), set(schema.get("required", []))


def _is_excluded_from_cli(meta: dict[str, Any]) -> bool:
    extra = meta.get("json_schema_extra", {}) if isinstance(meta, dict) else {}
    return bool(extra.get("exclude_from_cli"))


def _cli_name(field_name: str, meta: dict[str, Any]) -> str:
    extra = meta.get("json_schema_extra", {}) if isinstance(meta, dict) else {}
    return field_name.replace("_", "-") if extra.get("convert_underscores", True) else field_name


def _build_option(field_name: str, meta: dict[str, Any], is_required: bool) -> click.Option:
    cli = _cli_name(field_name, meta)
    help_text = meta.get("description", "")
    default = meta.get("default")
    enum_values = meta.get("enum")
    field_type = _resolve_field_type(meta)

    if field_type == "boolean":
        opt = click.Option([f"--{cli}/--no-{cli}"], is_flag=True, default=bool(default) if default is not None else False, help=help_text)
    elif field_type == "array":
        elem_type: Any = str
        items_meta = meta.get("items") if isinstance(meta.get("items"), dict) else None
        if items_meta:
            elem_type = _json_type_to_click_type(_resolve_field_type(items_meta))  # type: ignore[arg-type]
        opt = click.Option([f"--{cli}"], multiple=True, type=elem_type, required=is_required, help=help_text, default=tuple(default) if isinstance(default, list) else (), show_default=bool(default))
    else:
        click_type: Any = click.Choice([str(v) for v in enum_values]) if enum_values else _json_type_to_click_type(field_type)
        opt = click.Option([f"--{cli}"], type=click_type, required=is_required, default=default, help=help_text, show_default=default is not None)

    opt.name = field_name
    return opt


def _build_click_params(workflow_input_cls: type[WorkflowInput]) -> list[click.Parameter]:
    properties, required = _get_properties_and_required(workflow_input_cls)
    params: list[click.Parameter] = []
    for name, meta_any in properties.items():
        meta: dict[str, Any] = meta_any if isinstance(meta_any, dict) else {}
        if _is_excluded_from_cli(meta):
            continue
        is_required = name in required and meta.get("default") is None
        params.append(_build_option(name, meta, is_required))
    return params


def _normalize_array_options(kwargs: dict[str, Any], workflow_input_cls: type[WorkflowInput]) -> dict[str, Any]:
    properties, _ = _get_properties_and_required(workflow_input_cls)
    normalized: dict[str, Any] = {}
    for key, value in kwargs.items():
        meta: dict[str, Any] = properties.get(key, {}) if isinstance(properties.get(key, {}), dict) else {}
        if _resolve_field_type(meta) == "array" and isinstance(value, tuple):
            normalized[key] = list(value)
        else:
            normalized[key] = value
    return normalized


def _create_inputs(workflow_input_cls: type[WorkflowInput], command_name: str, values: dict[str, Any]) -> WorkflowInput:
    values["cli_command_name"] = command_name
    try:
        return workflow_input_cls(**values)
    except ValidationError as e:
        raise click.ClickException(f"Input validation failed:\n{e}")


def _clone_workflow(template: Workflow) -> Workflow:
    return copy.deepcopy(template)


def build_click_command_for_workflow(command_name: str, workflow_template: Workflow, workflow_input_cls: type[WorkflowInput]) -> click.Command:
    params = _build_click_params(workflow_input_cls)

    def _callback(**kwargs: Any) -> None:
        normalized = _normalize_array_options(kwargs, workflow_input_cls)
        inputs = _create_inputs(workflow_input_cls, command_name, normalized)
        wf = _clone_workflow(workflow_template)
        wf.inputs = inputs
        wf.init_by_cli()

    return click.Command(name=command_name, params=params, callback=_callback, help=f"Execute the {command_name} workflow.")



def build_click_group_with_commands(commands: dict[str, tuple[Workflow, type[WorkflowInput]]]) -> click.Group:
    group = click.Group(help="FluxCLI Framework Runner")
    for command_name, (workflow_template, wf_input_cls) in commands.items():
        group.add_command(build_click_command_for_workflow(command_name, workflow_template, wf_input_cls), name=command_name)
    return group

