import json
import unittest

from fluxly.node import Node, NodeExecution, NodeOutput
from fluxly.workflow import Workflow, WorkflowInput, WorkflowOutput


class SampleOutput(NodeOutput):
    value: str = ""


class SampleExecution(NodeExecution):
    output: SampleOutput = SampleOutput()


class SampleNode(Node):
    result: str = "done"

    def _create_execution(self) -> SampleExecution:
        return SampleExecution()

    def _logic(self) -> None:
        self.current_execution.output.value = self.result


class WorkflowOutputTest(unittest.TestCase):
    def test_workflow_summary_preserves_node_output(self) -> None:
        node = SampleNode(name="sample", result="hello")
        wf = Workflow(
            name="output-test",
            description="workflow output serialization",
            version="1.0",
            inputs=WorkflowInput(verbose=False),
        )
        wf.add_node(node)
        wf.execute()

        payload = json.loads(wf.last_execution.model_dump_json())
        executions = payload["output"]["node_to_executions"]["sample"]
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0]["output"]["value"], "hello")

    def test_workflow_output_model_preserves_subclass_executions(self) -> None:
        execution = SampleExecution()
        execution.output.value = "stored"

        workflow_output = WorkflowOutput()
        workflow_output.node_to_executions["sample"] = [execution]

        payload = json.loads(workflow_output.model_dump_json())
        self.assertEqual(
            payload["node_to_executions"]["sample"][0]["output"]["value"],
            "stored",
        )


if __name__ == "__main__":
    unittest.main()
