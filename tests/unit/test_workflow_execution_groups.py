import time
import unittest

from flowcli.exceptions import DataErrorException
from flowcli.node import Node
from flowcli.status import StatusCodes
from flowcli.workflow import Workflow, WorkflowInput


class SlowOk(Node):
    sleep_seconds: float = 0.3
    def _logic(self) -> None:
        time.sleep(self.sleep_seconds)


class FailFast(Node):
    def _logic(self) -> None:
        raise DataErrorException()


class ExecutionGroupsTest(unittest.TestCase):
    def _wf(self) -> Workflow:
        return Workflow(name="eg-wf", description="exec groups", version="v", inputs=WorkflowInput(verbose=False))

    def test_partial_success_across_groups_completes_workflow(self) -> None:
        wf = self._wf()

        slow_ok = SlowOk(name="slow-ok", sleep_seconds=0.4)
        fail_fast = FailFast(name="fail-fast")
        ok2 = SlowOk(name="ok2", sleep_seconds=0.05)

        wf.add_node(slow_ok)
        wf.add_node(fail_fast)
        wf.add_node(ok2)

        # Define execution groups
        wf.add_execution_group([slow_ok, fail_fast])
        wf.add_execution_group([ok2])

        # Ensure group 2 runs only after slow_ok completes successfully
        wf._graph.add_edge_if_source_completed(slow_ok, ok2)

        wf.execute()

        # Workflow should complete even if one node in Group 1 failed,
        # because Group 2 has a successful node and not all groups are "dead".
        self.assertEqual(wf.last_execution.status, StatusCodes.COMPLETED)

        # Assert node outcomes
        self.assertEqual(slow_ok.last_execution.status, StatusCodes.COMPLETED)
        self.assertEqual(ok2.last_execution.status, StatusCodes.COMPLETED)
        self.assertNotEqual(fail_fast.last_execution.status, StatusCodes.COMPLETED)

    def test_all_groups_have_failure_causes_workflow_failure(self) -> None:
        wf = self._wf()

        slow_ok_1 = SlowOk(name="slow-ok-1", sleep_seconds=0.3)
        fail_fast_1 = FailFast(name="fail-fast-1")
        fail_fast_2 = FailFast(name="fail-fast-2")

        wf.add_node(slow_ok_1)
        wf.add_node(fail_fast_1)
        wf.add_node(fail_fast_2)

        # Two groups, each will have a failing node
        wf.add_execution_group([slow_ok_1, fail_fast_1])
        wf.add_execution_group([fail_fast_2])

        # Delay the second group's start until slow_ok_1 completes,
        # to make failure ordering deterministic
        wf._graph.add_edge_if_source_completed(slow_ok_1, fail_fast_2)

        with self.assertRaises(DataErrorException):
            wf.execute()

        # Workflow status should reflect failure
        self.assertEqual(wf.last_execution.status, StatusCodes.DATA_ERROR)


if __name__ == "__main__":
    unittest.main()


