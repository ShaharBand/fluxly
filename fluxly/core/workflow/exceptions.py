from fluxly.core.exceptions import WorkflowException
from fluxly.core.status import StatusCodes


class NodesNotFoundException(WorkflowException):
    exit_code = StatusCodes.PREREQUISITE_FAIL


class UnsupportedGraphScenario(WorkflowException):
    exit_code = StatusCodes.PREREQUISITE_FAIL
