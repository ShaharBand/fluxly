import time
import unittest

from fluxcli.exceptions import DataErrorException, TimeoutException
from fluxcli.node import Node
from fluxcli.status import StatusCodes


class FlakyNode(Node):
    fail_times: int = 1

    def _logic(self) -> None:
        if self.attempt <= self.fail_times:
            raise DataErrorException("transient failure")


class AlwaysFailNode(Node):
    def _logic(self) -> None:
        raise DataErrorException("permanent failure")


class TimeoutNode(Node):
    def _logic(self) -> None:
        time.sleep((self.timeout_seconds or 1) + 1)


class NodeExecutionTest(unittest.TestCase):
    def test_retry_success_then_complete(self) -> None:
        node = FlakyNode(name="flaky", fail_times=1, max_retries=2, retry_delay_seconds=1)
        node.execute()

        self.assertEqual(node.attempt, 2)
        self.assertEqual(len(node.executions), 2)

        first, second = node.executions[0], node.executions[1]
        self.assertEqual(first.status, StatusCodes.DATA_ERROR)
        self.assertIsNotNone(first.error)
        self.assertEqual(second.status, StatusCodes.COMPLETED)

    def test_retry_exhausted_raises(self) -> None:
        node = AlwaysFailNode(name="always-fail", max_retries=3, retry_delay_seconds=1)
        with self.assertRaises(DataErrorException):
            node.execute()

        self.assertEqual(node.attempt, 3)
        self.assertEqual(len(node.executions), 3)
        for ex in node.executions:
            self.assertEqual(ex.status, StatusCodes.DATA_ERROR)
            self.assertIsNotNone(ex.error)

    def test_timeout_sets_status_and_raises(self) -> None:
        node = TimeoutNode(name="timeout", timeout_seconds=1, max_retries=1)
        with self.assertRaises(TimeoutException):
            node.execute()

        self.assertEqual(node.attempt, 1)
        self.assertEqual(len(node.executions), 1)
        latest = node.executions[-1]
        self.assertEqual(latest.status, StatusCodes.TIMED_OUT)
        self.assertIsNotNone(latest.error)
        self.assertEqual(latest.error.exception_class_name, "TimeoutException")


if __name__ == "__main__":
    unittest.main()


