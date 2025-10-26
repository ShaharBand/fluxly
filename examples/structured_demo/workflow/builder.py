from examples.structured_demo.nodes.alpha.node import Alpha
from examples.structured_demo.nodes.beta.node import Beta
from examples.structured_demo.workflow.input import DemoWorkflowInput
from fluxly.core.workflow.workflow import Workflow


def build_demo_workflow() -> Workflow:
    workflow = Workflow(name="structured_demo", description="Structured demo workflow", version="0.1")

    alpha = Alpha(name="Alpha", description="Echoes a message", timeout_seconds=5)
    beta = Beta(name="Beta", description="Appends a suffix", timeout_seconds=5)

    workflow.add_node(alpha)
    workflow.add_node(beta)
    workflow.add_edge(alpha, beta)
    workflow.add_execution_group([beta])

    workflow.inputs = DemoWorkflowInput(
        verbose=True,
        timeout_seconds=30,
        max_retries=1,
        retry_delay_seconds=0,
        auto_generate_md=False,
    )

    return workflow
