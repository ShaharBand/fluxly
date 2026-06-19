import json
import unittest
from typing import Annotated

from pydantic import Field

from fluxly.node import Node, NodeExecution, NodeOutput
from fluxly.workflow import Workflow, WorkflowInput, WorkflowOutput


class SampleOutput(NodeOutput):
    value: str = ""


class SampleExecution(NodeExecution):
    output: SampleOutput = SampleOutput()
    metric: Annotated[str, Field(description="Custom execution metric")] = ""


class CustomInput(WorkflowInput):
    token: str = "abc"


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
        execution.metric = "latency_ms=12"

        workflow_output = WorkflowOutput()
        workflow_output.node_to_executions["sample"] = [execution]

        payload = json.loads(workflow_output.model_dump_json())
        stored = payload["node_to_executions"]["sample"][0]
        self.assertEqual(stored["output"]["value"], "stored")
        self.assertEqual(stored["metric"], "latency_ms=12")

    def test_workflow_inputs_preserve_subclass_fields_on_dump(self) -> None:
        wf = Workflow(
            name="input-test",
            description="workflow input serialization",
            version="1.0",
            inputs=CustomInput(token="secret", verbose=False),
        )

        payload = json.loads(wf.model_dump_json())
        self.assertEqual(payload["inputs"]["token"], "secret")


if __name__ == "__main__":
    unittest.main()
