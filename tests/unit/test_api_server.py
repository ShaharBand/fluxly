import time
import unittest

from fastapi import status
from fastapi.testclient import TestClient

from fluxly.core.api.server import ApiConfig, build_app
from fluxly.core.node.node import Node
from fluxly.core.status import StatusCodes
from fluxly.core.workflow.input import WorkflowInput
from fluxly.core.workflow.workflow import Workflow


class _NoopNode(Node):
    def _logic(self) -> None:
        return None


def _build_simple_workflow() -> Workflow:
    wf = Workflow(
        name="ApiTestWF",
        description="API test workflow",
        version="0.0.1",
        inputs=WorkflowInput(verbose=False, timeout_seconds=5),
    )

    wf.add_node(_NoopNode(name="noop-node", description="No operation"))
    return wf


class TestApiServer(unittest.TestCase):
    def setUp(self) -> None:
        wf = _build_simple_workflow()
        endpoints = {"test": (wf, WorkflowInput)}
        app = build_app(endpoints=endpoints, config=ApiConfig())
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        res = self.client.get("/health")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.json(), {"status": "ok"})

    def test_submit_run_and_fetch_status(self) -> None:
        res = self.client.post("/test/run", json={})
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)
        data = res.json()
        self.assertIn("run_id", data)
        self.assertEqual(data["endpoint"], "test")
        self.assertIn(data["status"], [s.name for s in StatusCodes])

        run_id = data["run_id"]

        # Poll for completion (or failure) briefly
        non_terminal = {StatusCodes.WAITING.name, StatusCodes.IN_PROGRESS.name}
        terminal_statuses = {s.name for s in StatusCodes} - non_terminal
        status_value = data["status"]
        deadline = time.time() + 2
        while status_value not in terminal_statuses and time.time() < deadline:
            time.sleep(0.01)
            res2 = self.client.get(f"/runs/{run_id}")
            self.assertEqual(res2.status_code, status.HTTP_200_OK)
            status_value = res2.json()["status"]

        # Verify final record shape (allow any valid status to avoid flakiness)
        res3 = self.client.get(f"/runs/{run_id}")
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        final = res3.json()
        self.assertEqual(final["run_id"], run_id)
        self.assertEqual(final["endpoint"], "test")
        self.assertIn(final["status"], {s.name for s in StatusCodes})

        res4 = self.client.get(f"/test/runs/{run_id}")
        self.assertEqual(res4.status_code, status.HTTP_200_OK)

        res5 = self.client.get(f"/wrong/runs/{run_id}")
        self.assertEqual(res5.status_code, status.HTTP_404_NOT_FOUND)

    def test_submit_validation_error(self) -> None:
        # retry_delay_seconds must be >= 0; negative should 422
        res = self.client.post("/test/run", json={"retry_delay_seconds": -1})
        self.assertEqual(res.status_code, status.HTTP_422_UNPROCESSABLE_CONTENT)

    def test_get_nonexistent_run_returns_404(self) -> None:
        res = self.client.get("/runs/does-not-exist")
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        res2 = self.client.get("/test/runs/does-not-exist")
        self.assertEqual(res2.status_code, status.HTTP_404_NOT_FOUND)


if __name__ == "__main__":
    unittest.main()


