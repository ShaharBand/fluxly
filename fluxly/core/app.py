import sys

from pydantic import BaseModel, PrivateAttr

from fluxly.core.api.server import ApiConfig, serve
from fluxly.core.cli.generator import build_click_group_with_commands
from fluxly.core.workflow.input import WorkflowInput
from fluxly.core.workflow.workflow import Workflow


class Fluxly(BaseModel):
    # TODO: debug: bool = False
    # TODO: max_workers: int | None = None
    _endpoints: dict[str, tuple[Workflow, type[WorkflowInput]]] = PrivateAttr(default_factory=dict)
    _api_config: ApiConfig = PrivateAttr(default_factory=ApiConfig)

    def add_endpoint(self, endpoint_name: str, workflow: Workflow, workflow_input_cls: type[WorkflowInput]) -> None:
        if endpoint_name in self._endpoints:
            raise ValueError(f"Endpoint {endpoint_name} already registered")
        if not isinstance(workflow, Workflow):
            raise TypeError("workflow must be a Workflow instance (pre-built with nodes and edges)")
        self._endpoints[endpoint_name] = (workflow, workflow_input_cls)

    def add_command(self, endpoint_name: str, workflow: Workflow, workflow_input_cls: type[WorkflowInput]) -> None:
        self.add_endpoint(endpoint_name, workflow, workflow_input_cls)

    def configure_api(self, config: ApiConfig) -> None:
        self._api_config = config

    def run_api(self) -> None:
        serve(self._endpoints, self._api_config)

    def run_cli(self) -> None:
        click_group = build_click_group_with_commands(self._endpoints)
        click_group()

    def run(self) -> None:
        if len(sys.argv) > 1:
            self.run_cli()
        else:
            self.run_api()

