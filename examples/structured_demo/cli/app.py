from flowcli import FlowCLI

from examples.structured_demo.workflow.builder import build_demo_workflow
from examples.structured_demo.workflow.input import DemoWorkflowInput


def main() -> None:
    wf = build_demo_workflow()
    cli = FlowCLI()
    cli.add_command("structured-demo", wf, DemoWorkflowInput)
    cli.run()


if __name__ == "__main__":
    main()



