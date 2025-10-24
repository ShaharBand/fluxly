import unittest

from fluxcli.node import Node, NodeExecution, NodeOutput
from fluxcli.status import StatusCodes
from fluxcli.workflow import Workflow, WorkflowInput


class ProducerOutput(NodeOutput):
    value: str = ""


class ProducerExecution(NodeExecution):
    output: ProducerOutput = ProducerOutput()


class Producer(Node):
    produced_value: str = "alpha"

    def _create_execution(self) -> ProducerExecution:
        return ProducerExecution()

    def _logic(self) -> None:
        self.current_execution.output.value = self.produced_value


class ConsumerOutput(NodeOutput):
    seen: str = ""


class ConsumerExecution(NodeExecution):
    output: ConsumerOutput = ConsumerOutput()


class Consumer(Node):
    producer_node: Producer | None = None

    def _create_execution(self) -> ConsumerExecution:
        return ConsumerExecution()

    def _logic(self) -> None:
        assert self.producer_node is not None, "Producer node must be provided before running Consumer"
        self.current_execution.output.seen = self.producer_node.last_execution.output.value


class Node2NodeCommunicationTest(unittest.TestCase):
    def _wf(self, nodes: list[Node]) -> Workflow:
        wf = Workflow(
            name="n2n",
            description="node to node",
            inputs=WorkflowInput(verbose=False),
        )
        for n in nodes:
            wf.add_node(n)
        return wf

    def test_consumer_reads_actual_producer_execution_value(self) -> None:
        producer = Producer(name="producer", produced_value="from-execution")
        consumer = Consumer(name="consumer", producer_node=producer)

        wf = self._wf([producer, consumer])
        wf.add_edge_if_source_completed(producer, consumer)
        wf.execute()

        self.assertEqual(producer.last_execution.status, StatusCodes.COMPLETED)
        self.assertEqual(consumer.last_execution.status, StatusCodes.COMPLETED)
        self.assertEqual(consumer.last_execution.output.seen, "from-execution")
        self.assertIs(consumer.producer_node, producer)
        consumer.producer_node.last_execution.output.value = "mutated"
        self.assertEqual(producer.last_execution.output.value, "mutated")


if __name__ == "__main__":
    unittest.main()


