FluxCLI provides **typed exceptions** to give precise **exit-code and status control**.  
Raise these inside nodes (or workflows) to set both **runtime status** and **process exit code** consistently.

---

### Built-in Exceptions

| Exception | Status Code |
|-----------|------------|
| `TimeoutException` | `StatusCodes.TIMED_OUT` |
| `InfrastructureErrorException` | `StatusCodes.INFRASTRUCTURE_ERROR` |
| `DataErrorException` | `StatusCodes.DATA_ERROR` |
| `PrerequisiteFailureException` | `StatusCodes.PREREQUISITE_FAIL` |
| `APICallFailureException` | `StatusCodes.API_CALL_FAILURE` |
| `NetworkFailureException` | `StatusCodes.NETWORK_FAILURE` |
| `DataValidationFailureException` | `StatusCodes.DATA_VALIDATION_FAILURE` |
| `DependencyUnavailableException` | `StatusCodes.DEPENDENCY_UNAVAILABLE` |

---

### Usage Inside a Node

!!! code "Node Exception Example"
    ```python
    from fluxcli.node import Node
    from fluxcli.exceptions import DataValidationFailureException

    class Validate(Node):
        def _is_valid_input(self) -> bool:
            return False

        def _logic(self) -> None:
            if not self._is_valid_input():
                raise DataValidationFailureException("Invalid input payload")
    ```

---

### Custom Exceptions

You can define custom exceptions by subclassing `WorkflowException`.  
Make sure to set an **exit code** using a `StatusCodes` Enum value.

!!! code "Custom Exception Example"
    ```python
    from enum import Enum
    from fluxcli.exceptions import WorkflowException
    from fluxcli.status import StatusCodes

    class BusinessRuleViolation(WorkflowException):
        exit_code: Enum = StatusCodes.DATA_ERROR
    ```

!!! note "Rules for Custom Exceptions"
- Exit codes must be **validated integers (0–255)**.  
- Raising a `WorkflowException` marks the **current node attempt** with that status.  
- Workflow execution propagates the **consistent status and exit code** downstream.
