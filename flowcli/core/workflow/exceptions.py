from flowcli.core.exceptions import WorkflowException
from flowcli.core.status import StatusCodes


class NodesNotFoundException(WorkflowException):
    exit_code = StatusCodes.PREREQUISITE_FAIL


class UnsupportedGraphScenario(WorkflowException):
    exit_code = StatusCodes.PREREQUISITE_FAIL
