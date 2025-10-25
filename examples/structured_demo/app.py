from examples.structured_demo.workflow.builder import build_demo_workflow
from examples.structured_demo.workflow.input import DemoWorkflowInput
from fluxly import Fluxly


def main() -> None:
    wf = build_demo_workflow()
    cli = Fluxly()
    cli.add_endpoint("structured-demo", wf, DemoWorkflowInput)
    cli.run()


if __name__ == "__main__":
    main()



