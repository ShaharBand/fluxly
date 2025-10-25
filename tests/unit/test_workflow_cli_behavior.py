import os
import sys
import unittest

from fluxly import Fluxly
from fluxly.exceptions import DataErrorException
from fluxly.node import Node
from fluxly.status import StatusCodes
from fluxly.workflow import Workflow, WorkflowInput


class OkNode(Node):
    def _logic(self) -> None:
        pass


class FailNode(Node):
    def _logic(self) -> None:
        raise DataErrorException()


def _build_cli(cmd_name: str, node: Node) -> Fluxly:
    wf = Workflow(name="test-cli-wf", description="cli test workflow", inputs=WorkflowInput(verbose=False))
    wf.add_node(node)
    cli = Fluxly()
    cli.add_command(cmd_name, wf, WorkflowInput)
    return cli


class FluxlyCliTest(unittest.TestCase):
    def setUp(self) -> None:
        self._orig_argv = list(sys.argv)

    def tearDown(self) -> None:
        sys.argv = self._orig_argv

    def test_cli_success_exit_code_zero(self) -> None:
        cli = _build_cli("ok", OkNode(name="ok-node"))
        sys.argv = ["prog", "ok"]
        with self.assertRaises(SystemExit) as ctx:
            cli.run_cli()
        self.assertEqual(ctx.exception.code, 0)


    def test_cli_failure_exit_code_custom(self) -> None:
        cli = _build_cli("fail", FailNode(name="fail-node"))
        sys.argv = ["prog", "fail"]
        with self.assertRaises(SystemExit) as ctx:
            cli.run_cli()
        self.assertEqual(ctx.exception.code, StatusCodes.DATA_ERROR.value)



    def test_cli_env_only_params_are_applied(self) -> None:
        class AssertInputsNode(Node):
            def _logic(self) -> None:
                assert self._workflow_input is not None
                assert self._workflow_input.max_retries == 2
                assert self._workflow_input.retry_delay_seconds == 1
                assert self._workflow_input.timeout_seconds == 5
                assert self._workflow_input.md_file_path == "env_doc.md"
                assert self._workflow_input.diagram_file_path == "env_diagram.png"

        cli = _build_cli("ok", AssertInputsNode(name="assert-inputs"))

        prev_env = {
            "FLUXLY_MAX_RETRIES": os.environ.get("FLUXLY_MAX_RETRIES"),
            "FLUXLY_RETRY_DELAY_SECONDS": os.environ.get("FLUXLY_RETRY_DELAY_SECONDS"),
            "FLUXLY_TIMEOUT_SECONDS": os.environ.get("FLUXLY_TIMEOUT_SECONDS"),
            "FLUXLY_MD_FILE_PATH": os.environ.get("FLUXLY_MD_FILE_PATH"),
            "FLUXLY_DIAGRAM_FILE_PATH": os.environ.get("FLUXLY_DIAGRAM_FILE_PATH"),
        }

        os.environ["FLUXLY_MAX_RETRIES"] = "2"
        os.environ["FLUXLY_RETRY_DELAY_SECONDS"] = "1"
        os.environ["FLUXLY_TIMEOUT_SECONDS"] = "5"
        os.environ["FLUXLY_MD_FILE_PATH"] = "env_doc.md"
        os.environ["FLUXLY_DIAGRAM_FILE_PATH"] = "env_diagram.png"

        try:
            sys.argv = ["prog", "ok"]
            with self.assertRaises(SystemExit) as ctx:
                cli.run_cli()
            self.assertEqual(ctx.exception.code, 0)
        finally:
            for k, v in prev_env.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

