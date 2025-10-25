from enum import Enum

from fluxly.core.status import StatusCodes


class WorkflowException(Exception):
    exit_code: Enum | int | None = None

    def __init__(self, message: str = ""):
        if not isinstance(self.exit_code, Enum):
            raise TypeError(f"WorkflowException exit_code must be an instance of Enum, Actual: {type(self.exit_code).__name__}")

        if not (0 <= self.exit_code.value <= 255):
            raise ValueError(f"WorkflowException exit_code value must be between 0 and 255, Actual: {self.exit_code.value}")

        super().__init__(message)

class TimeoutException(WorkflowException):
    exit_code: Enum = StatusCodes.TIMED_OUT

class InfrastructureErrorException(WorkflowException):
    exit_code: Enum = StatusCodes.INFRASTRUCTURE_ERROR

class DataErrorException(WorkflowException):
    exit_code: Enum = StatusCodes.DATA_ERROR

class PrerequisiteFailureException(WorkflowException):
    exit_code: Enum = StatusCodes.PREREQUISITE_FAIL

class APICallFailureException(WorkflowException):
    exit_code: Enum = StatusCodes.API_CALL_FAILURE

class NetworkFailureException(WorkflowException):
    exit_code: Enum = StatusCodes.NETWORK_FAILURE

class DataValidationFailureException(WorkflowException):
    exit_code: Enum = StatusCodes.DATA_VALIDATION_FAILURE

class DependencyUnavailableException(WorkflowException):
    exit_code: Enum = StatusCodes.DEPENDENCY_UNAVAILABLE
