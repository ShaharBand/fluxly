# 🕹️ Workflow:

## ⚙️ Workflow Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | complex-demo |
| **Description**  | Complex DAG for docs/diagram demo |
| **Version**  | 0.1 |
| **Total Nodes Count**  | 10 |
| **Execution Groups Count**  | 2 |


## 📝 Workflow Input
| Attribute | Description | Default | Required | Type | Value | Additional Tags |
|-----------|-------------|---------|----------|------|-------|----------------|
| **cli-command-name** | CLI command name for the workflow. | None | False | string, null | None | exclude_from_cli |
| **verbose** | Print more details for debug | True | False | boolean | False | None |
| **timeout-seconds** | Timeout for the workflow in seconds. | None | False | integer, null | None | None |
| **max-retries** | Maximum number of run attempts allowed in case of failure. | 0 | False | integer | 0 | None |
| **retry-delay-seconds** | Delay between retries in seconds. | 0 | False | integer | 0 | None |
| **auto-generate-md** | Automatically generate markdown file for the workflow input documentation | False | False | boolean | True | None |
| **md-file-path** | Path to save the generated markdown file. | workflow_documentation.md | False | string | docs/complex_workflow.md | None |
| **diagram-file-path** | Path to save the generated workflow graph diagram image (png). | workflow_diagram.png | False | string | docs/imgs/complex_workflow.png | None |


## 📊 Workflow Metadata
| Attribute | Description | Default | Required | Type | Value | Additional Tags |
|-----------|-------------|---------|----------|------|-------|----------------|
| **start-time** | Start datetime of the workflow execution. | None | False | string, null | 2025-10-22 21:38:33.676 | None |
| **end-time** | End datetime of the workflow execution. | None | False | string, null | 2025-10-22 21:38:33.765 | None |
## 📤 Workflow Output
| Attribute | Description | Default | Required | Type | Value | Additional Tags |
|-----------|-------------|---------|----------|------|-------|----------------|
| **status** | Workflow execution status | 21 | False | Unknown | StatusCodes.WAITING | None |
| **nodes-executions** | Workflow nodes executions | [] | False | array | [{'metadata': {'start_time': '2025-10-22 21:38:33.683', 'end_time': '2025-10-22 21:38:33.708', 'process_time': '0h 0m 0s 25ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.708', 'end_time': '2025-10-22 21:38:33.715', 'process_time': '0h 0m 0s 6ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.715', 'end_time': '2025-10-22 21:38:33.715', 'process_time': '0h 0m 0s 0ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.721', 'end_time': '2025-10-22 21:38:33.727', 'process_time': '0h 0m 0s 6ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.727', 'end_time': '2025-10-22 21:38:33.727', 'process_time': '0h 0m 0s 0ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.728', 'end_time': '2025-10-22 21:38:33.728', 'process_time': '0h 0m 0s 0ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.728', 'end_time': '2025-10-22 21:38:33.746', 'process_time': '0h 0m 0s 18ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.746', 'end_time': '2025-10-22 21:38:33.765', 'process_time': '0h 0m 0s 18ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.765', 'end_time': '2025-10-22 21:38:33.765', 'process_time': '0h 0m 0s 0ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}, {'metadata': {'start_time': '2025-10-22 21:38:33.765', 'end_time': '2025-10-22 21:38:33.765', 'process_time': '0h 0m 0s 0ms'}, 'status': <StatusCodes.COMPLETED: 0>, 'output': {}, 'error': None}] | None |






# 👾 Nodes:



## 🖼️ Nodes Diagram

![Nodes Diagram](docs/imgs/complex_workflow.png)

# 👾 Node 1# - ingest

## ⚙️ Step 1# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | ingest |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 2# - validate

## ⚙️ Step 2# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | validate |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 3# - transform-a

## ⚙️ Step 3# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | transform-a |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 4# - transform-b

## ⚙️ Step 4# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | transform-b |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 5# - join

## ⚙️ Step 5# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | join |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 6# - enrich

## ⚙️ Step 6# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | enrich |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 7# - analyze

## ⚙️ Step 7# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | analyze |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 8# - report

## ⚙️ Step 8# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | report |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 9# - archive

## ⚙️ Step 9# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | archive |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


# 👾 Node 10# - notify

## ⚙️ Step 10# - Configuration
| Attribute   | Description                                   |
|-------------|-----------------------------------------------|
| **Name**  | notify |
| **Description**  | None |
| **Timeout (seconds)**  | None |
| **Max Retries**  | 0 |
| **Retry delay (seconds)**  | 0 |


