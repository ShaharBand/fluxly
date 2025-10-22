import time
import unittest

from flowcli.exceptions import (
    DataErrorException,
    TimeoutException,
)
from flowcli.node import Node
from flowcli.status import StatusCodes
from flowcli.workflow import Workflow, WorkflowInput


class OkNode(Node):
    def _logic(self) -> None:
        pass


class FailNode(Node):
    def _logic(self) -> None:
        raise DataErrorException("failure")


class SlowNode(Node):
    def _logic(self) -> None:
        time.sleep((self.timeout_seconds or 1) + 1)


class WorkflowBehaviorTest(unittest.TestCase):
    def _wf(self, node: Node, timeout_seconds: int | None = None) -> Workflow:
        inputs = WorkflowInput(verbose=False, timeout_seconds=timeout_seconds)
        wf = Workflow(
            name="test-workflow",
            description="test workflow",
            version="1.0",
            inputs=inputs
        )
        wf.add_node(node)
        return wf

    def test_success(self) -> None:
        wf = self._wf(OkNode(name="ok-node"))
        wf.execute()
        self.assertEqual(wf.last_execution.status, StatusCodes.COMPLETED)

    def test_retry_then_success(self) -> None:
        class Flaky(Node):
            fail_times: int = 1
            def _logic(self) -> None:
                if self.attempt <= self.fail_times:
                    raise DataErrorException("transient")

        node = Flaky(name="flaky", max_retries=2, retry_delay_seconds=0)
        wf = self._wf(node)
        wf.execute()
        self.assertEqual(node.attempt, 2)
        self.assertEqual(wf.last_execution.status, StatusCodes.COMPLETED)

    def test_failure_sets_status_and_raises(self) -> None:
        wf = self._wf(FailNode(name="fail"))
        with self.assertRaises(DataErrorException):
            wf.execute()
        self.assertEqual(wf.last_execution.status, StatusCodes.DATA_ERROR)

    def test_timeout_sets_status_and_raises(self) -> None:
        node = SlowNode(name="slow", timeout_seconds=1)
        wf = self._wf(node, timeout_seconds=1)
        with self.assertRaises(TimeoutException):
            wf.execute()
        self.assertEqual(wf.last_execution.status, StatusCodes.TIMED_OUT)


if __name__ == "__main__":
    unittest.main()


