from examples.etl_pipeline.workflow.builder import build_etl_workflow
from examples.etl_pipeline.workflow.input import EtlInput
from fluxly import Fluxly


def main() -> None:
    app = Fluxly()
    app.add_endpoint("etl", build_etl_workflow(), EtlInput)
    app.run()


if __name__ == "__main__":
    main()
