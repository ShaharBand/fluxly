import unittest

from flowcli.node import Node
from flowcli.workflow import WorkflowGraph


class NodeExecutionError(Exception):
    pass

class DummyNode(Node):
    fail: bool = False

    def _logic(self) -> None:
        if self.fail:
            raise NodeExecutionError(f"{self.name} failed")
        print(f"{self.name} executed successfully")


class WorkflowGraphTest(unittest.TestCase):
    def setUp(self) -> None:
        self.node_a = DummyNode(name="test-A")
        self.node_b = DummyNode(name="test-B")
        self.node_c = DummyNode(name="test-C")
        self.graph = WorkflowGraph()
        self.graph.add_node(self.node_a)
        self.graph.add_node(self.node_b)
        self.graph.add_node(self.node_c)

    def test_simple_dependency(self) -> None:
        self.graph.add_edge(self.node_a, self.node_b)
        completed = set()
        self.assertTrue(self.graph.can_node_run(self.node_a, completed))
        self.assertFalse(self.graph.can_node_run(self.node_b, completed))
        self.node_a.execute()
        completed.add(self.node_a)
        self.assertTrue(self.graph.can_node_run(self.node_b, completed))

    def test_acyclic_enforcement(self) -> None:
        self.graph.add_edge(self.node_a, self.node_b)
        self.graph.add_edge(self.node_b, self.node_c)
        with self.assertRaises(ValueError):
            self.graph.add_edge(self.node_c, self.node_a)

    def test_duplicate_node_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.graph.add_node(DummyNode(name="test-A"))

    def test_duplicate_edge_rejected(self) -> None:
        self.graph.add_edge(self.node_a, self.node_b)
        with self.assertRaises(ValueError):
            self.graph.add_edge(self.node_a, self.node_b)

    def test_conditional_edge(self) -> None:
        def condition():
            return True
        self.graph.add_conditional_edge(self.node_a, self.node_b, condition)
        completed = set()
        self.assertTrue(self.graph.can_node_run(self.node_a, completed))
        self.assertFalse(self.graph.can_node_run(self.node_b, completed))
        self.node_a.execute()
        completed.add(self.node_a)
        self.assertTrue(self.graph.can_node_run(self.node_b, completed))

    def test_failed_node(self) -> None:
        fail_node = DummyNode(name="Fail", fail=True)
        self.graph.add_node(fail_node)
        self.graph.add_conditional_edge(fail_node, self.node_c, condition=lambda: True)
        completed = set()
        with self.assertRaises(NodeExecutionError):
            fail_node.execute()
        completed.add(fail_node) # Regardless of the failure, the node should be considered completed
        self.assertTrue(self.graph.can_node_run(self.node_c, completed)) # The node should be able to run because the condition is met

    def test_edge_if_source_completed(self) -> None:
        self.graph.add_edge_if_source_completed(self.node_a, self.node_b)
        completed = set()
        self.assertTrue(self.graph.can_node_run(self.node_a, completed))
        self.assertFalse(self.graph.can_node_run(self.node_b, completed))

        self.node_a.execute()
        completed.add(self.node_a)
        self.assertTrue(self.graph.can_node_run(self.node_b, completed))


if __name__ == "__main__":
    unittest.main()
