import time

from flowcli.node import Node
from flowcli.workflow import Workflow, WorkflowInput


class NodeA(Node):
    def _logic(self) -> None:
        time.sleep(0.2)
        _demo_state["do_c"] = True


class NodeB(Node):
    def _logic(self) -> None:
        time.sleep(0.1)


class NodeC(Node):
    def _logic(self) -> None:
        time.sleep(0.1)

wf = Workflow(name="demo", description="Demo concurrent workflow", version="0.1")
a = NodeA(name="test A node", description="Root node", timeout_seconds=5)
b = NodeB(name="test B node", description="Runs after A", timeout_seconds=5, max_retries=2)
c = NodeC(name="test C node", description="Conditionally runs after A", timeout_seconds=5)
d = NodeC(name="test d node", description="runs after c", timeout_seconds=5)

_demo_state = {"do_c": False}


def build_demo_workflow() -> Workflow:
    wf.add_node(a)
    wf.add_node(b)
    wf.add_node(c)
    wf.add_node(d)

    wf.add_edge(a, b)
    wf.add_conditional_edge(a, c, condition=lambda: _demo_state["do_c"])
    wf.add_edge(c, d)
    return wf


if __name__ == "__main__":
    workflow = build_demo_workflow()
    workflow.inputs = WorkflowInput(verbose=True, timeout_seconds=30, max_retries=1, retry_delay_seconds=0, auto_generate_md=True)

    workflow.add_execution_group([a, b])
    workflow.execute()

    print(f"Workflow status: {workflow.last_execution.status} ")
    print(f"Workflow output: ({workflow.last_execution.output})")
