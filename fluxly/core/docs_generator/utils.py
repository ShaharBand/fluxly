from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from fluxly.core.workflow import Workflow

def sanitize_for_markdown(value: str) -> str:
    if isinstance(value, str):
        value = value.replace("\n", "<br>").replace("\r", "")
        value = value.replace("|", "\\|").replace("`", "\\`")
    return str(value)

def generate_markdown_table_from_dict(title: str, data_dict: dict) -> str:
    table = f"## {title}\n"
    table += "| Attribute   | Description                                   |\n"
    table += "|-------------|-----------------------------------------------|\n"

    for key, value in data_dict.items():
        table += f"| **{key}**  | {value} |\n"

    return table

def generate_markdown_table_from_basemodel(title: str, model: BaseModel | None) -> str:
    if model is None:
        return generate_markdown_table_from_dict(title, {"Info": "No data"})
    rows = []
    schema = model.model_json_schema()

    for parameter_name, parameter_configuration in schema.get('properties', {}).items():
        if parameter_configuration.get('exclude_from_documentation', False):
            continue

        formatted_parameter_name = parameter_name.replace('_', '-') if parameter_configuration.get('convert_underscores', True) else parameter_name
        parameters_required = schema.get('required', [])
        parameter_types = [parameter_configuration.get('type')] if 'type' in parameter_configuration else [
            param.get('type') for param in parameter_configuration.get('anyOf', [])
        ]
        model_dict = model.model_dump()
        field_value = model_dict.get(parameter_name, 'None')

        field_value = sanitize_for_markdown(str(field_value))

        additional_tags = []
        if parameter_configuration.get('convert_underscores', False):
            additional_tags.append("convert_underscores")
        if parameter_configuration.get('exclude_from_cli', False):
            additional_tags.append("exclude_from_cli")

        row = {
            'name': formatted_parameter_name,
            'description': parameter_configuration.get('description', 'None'),
            'default': parameter_configuration.get('default', 'None'),
            'required': "True" if parameter_name in parameters_required else "False",
            'type': ", ".join(filter(None, parameter_types)) if parameter_types else "Unknown",
            'value': field_value,  # Adding actual field value
            'additional_tags': ", ".join(additional_tags) if additional_tags else "None",
        }
        rows.append(row)

    table = f"## {title}\n"
    table += "| Attribute | Description | Default | Required | Type | Value | Additional Tags |\n"
    table += "|-----------|-------------|---------|----------|------|-------|----------------|\n"

    for row in rows:
        table += (f"| **{row['name']}** "
                  f"| {row['description']} "
                  f"| {row['default']} "
                  f"| {row['required']} "
                  f"| {row['type']} "
                  f"| {row['value']} "
                  f"| {row['additional_tags']} "
                  f"|\n")

    return table

def generate_graph_diagram(workflow: "Workflow", output_filename: str) -> None:
    # Resolve filename and output format (the diagrams library expects filename without extension)
    import importlib
    import os
    try:
        diagrams_mod = importlib.import_module("diagrams")
        languages_mod = importlib.import_module("diagrams.programming.language")
        Diagram = diagrams_mod.Diagram
        DiagramsEdge = diagrams_mod.Edge
        Python = languages_mod.Python
    except Exception:
        print("[DocsGenerator] Skipping diagram generation: diagrams library not available. Install it e.g.: pip install diagrams && brew install graphviz")
        return

    base_name = os.path.basename(output_filename)
    if "." in base_name:
        file_root, file_ext = os.path.splitext(output_filename)
        diagram_filename = file_root
        outformat = file_ext.lstrip(".") or "png"
    else:
        diagram_filename = output_filename
        outformat = "png"

    graph = workflow._graph

    try:
        with Diagram(f"{workflow.name} Nodes", filename=diagram_filename, outformat=outformat, show=False):
            diagram_nodes: dict[str, Python] = {}

            # Build node palette from workflow graph
            nodes_collection = workflow.get_nodes()
            node_names = [n.name for n in nodes_collection]

            for node_name in node_names:
                if node_name not in diagram_nodes:
                    diagram_nodes[node_name] = Python(node_name)

            # Draw edges from the graph
            for e in graph.edges:
                src_name = e.source
                dst_name = e.destination

                src_node = diagram_nodes.get(src_name) or Python(src_name)
                diagram_nodes[src_name] = src_node

                dst_node = diagram_nodes.get(dst_name) or Python(dst_name)
                diagram_nodes[dst_name] = dst_node

                if e.condition is not None:
                    src_node >> DiagramsEdge(label="Next Step with Condition", color="red", style="dashed") >> dst_node
                else:
                    src_node >> DiagramsEdge(label="Next Step", color="black") >> dst_node
    except Exception:
        print("[DocsGenerator] Skipping diagram generation: Graphviz not found. Install it e.g.: brew install graphviz")

