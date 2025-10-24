import sys
import unittest

from fluxcli import FluxCLI
from fluxcli.exceptions import DataErrorException
from fluxcli.node import Node
from fluxcli.status import StatusCodes
from fluxcli.workflow import Workflow, WorkflowInput


class OkNode(Node):
    def _logic(self) -> None:
        pass


class FailNode(Node):
    def _logic(self) -> None:
        raise DataErrorException()


def _build_cli(cmd_name: str, node: Node) -> FluxCLI:
    wf = Workflow(name="test-cli-wf", description="cli test workflow", inputs=WorkflowInput(verbose=False))
    wf.add_node(node)
    cli = FluxCLI()
    cli.add_command(cmd_name, wf, WorkflowInput)
    return cli


class FluxCLICliTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_argv = list(sys.argv)

    def tearDown(self) -> None:
        sys.argv = self._orig_argv

    def test_cli_success_exit_code_zero(self) -> None:
        cli = _build_cli("ok", OkNode(name="ok-node"))
        sys.argv = ["prog", "ok"]
        with self.assertRaises(SystemExit) as ctx:
            cli.run()
        self.assertEqual(ctx.exception.code, 0)


    def test_cli_failure_exit_code_custom(self) -> None:
        cli = _build_cli("fail", FailNode(name="fail-node"))
        sys.argv = ["prog", "fail"]
        with self.assertRaises(SystemExit) as ctx:
            cli.run()
        self.assertEqual(ctx.exception.code, StatusCodes.DATA_ERROR.value)



