from examples.etl_pipeline.nodes.extract.node import Extract
from examples.etl_pipeline.nodes.load.node import Load
from examples.etl_pipeline.nodes.transform.node import Transform
from fluxly.workflow import Workflow


def build_etl_workflow() -> Workflow:
    workflow = Workflow(
        name="etl_pipeline",
        description="Extract, transform, load users",
        version="1.0",
    )

    extract = Extract(
        name="extract",
        description="Pull records from the source API",
        timeout_seconds=30,
    )
    transform = Transform(
        name="transform",
        description="Normalize records",
        extract=extract,
    )
    load = Load(
        name="load",
        description="Write records to the warehouse",
        transform=transform,
        max_retries=2,
    )

    workflow.add_node(extract)
    workflow.add_node(transform)
    workflow.add_node(load)
    workflow.add_edge(extract, transform)
    workflow.add_edge(transform, load)
    workflow.add_execution_group([load])

    return workflow
