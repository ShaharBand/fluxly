from typing import TYPE_CHECKING

from flowcli.core.docs_generator.utils import (
    generate_graph_diagram,
    generate_markdown_table_from_basemodel,
    generate_markdown_table_from_dict,
)

if TYPE_CHECKING:
    from flowcli.core.workflow import Workflow

def generate_workflow_documentation(workflow: "Workflow",
                                  md_output_path: str = "workflow_documentation.md",
                                  diagram_output_path: str = "workflow_diagram.png") -> None:
    amount_of_nodes = len(workflow.get_nodes())
    amount_of_execution_groups = len(workflow.get_execution_groups())

    workflow_config = {
        "Name": workflow.name,
        "Description": workflow.description,
        "Version": workflow.version,
        "Total Nodes Count": amount_of_nodes,
        "Execution Groups Count": amount_of_execution_groups,
    }

    workflow_config_table = generate_markdown_table_from_dict('⚙️ Workflow Configuration', workflow_config)
    workflow_input_table = generate_markdown_table_from_basemodel('📝 Workflow Input', workflow.inputs)

    execution_tables: list[str] = []
    if workflow.attempt > 0:
        current = workflow.current_execution
        workflow_metadata_table = generate_markdown_table_from_basemodel('📊 Workflow Metadata', current.metadata)
        workflow_output_table = generate_markdown_table_from_basemodel('📤 Workflow Output', current.output)
        execution_tables.extend([workflow_metadata_table, workflow_output_table])
    else:
        execution_tables.append(
            generate_markdown_table_from_dict('📊 Workflow Executions', {"Info": "No executions yet"})
        )

    generate_graph_diagram(workflow=workflow, output_filename=diagram_output_path)

    node_tables = []
    for idx, node in enumerate(workflow.get_nodes(), start=1):
        node_config = {
            "Name": node.name,
            "Description": node.description,
            "Timeout (seconds)": node.timeout_seconds,
            "Max Retries": node.max_retries,
            "Retry delay (seconds)": node.retry_delay_seconds,
        }

        node_config_table = generate_markdown_table_from_dict(f'⚙️ Step {idx}# - Configuration', node_config)

        node_tables.append(f"# 👾 Node {idx}# - {node.name}")
        node_tables.append(node_config_table)

    nodes_markdown = "\n\n".join(node_tables)

    markdown_content = (
        f"# 🕹️ Workflow:\n\n"
        f"{workflow_config_table}\n\n"
        f"{workflow_input_table}\n\n"
        f"{''.join(execution_tables)}\n\n"
        f"\n\n\n\n# 👾 Nodes:\n\n"
        f"\n\n## 🖼️ Nodes Diagram\n\n![Nodes Diagram]({diagram_output_path})\n\n"
        f"{nodes_markdown}\n\n"

    )

    with open(md_output_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)

    print(f"Markdown file '{md_output_path}' generated successfully!")
