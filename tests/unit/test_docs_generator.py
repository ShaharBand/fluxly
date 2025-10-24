import os
import tempfile
import unittest

from fluxcli.core.docs_generator.generator import generate_workflow_documentation
from fluxcli.core.node.node import Node
from fluxcli.core.workflow.input import WorkflowInput
from fluxcli.core.workflow.workflow import Workflow


class _NoopNode(Node):
    def _logic(self) -> None:
        return None


def _build_simple_workflow() -> Workflow:
    wf = Workflow(
        name="DocsGenWF",
        description="Docs generator test",
        version="0.1.0",
        inputs=WorkflowInput(cli_command_name="docs-gen-wf", auto_generate_md=False),
    )

    n1 = _NoopNode(name="A-test", description="First")
    n2 = _NoopNode(name="B-test", description="Second")

    wf.add_node(n1)
    wf.add_node(n2)
    wf.add_edge(n1, n2)

    return wf


class TestDocsGenerator(unittest.TestCase):
    def test_generate_workflow_documentation_creates_markdown_and_references_sections(self) -> None:
        wf = _build_simple_workflow()

        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = os.path.join(tmpdir, "wf.md")
            diagram_path = os.path.join(tmpdir, "wf.png")

            generate_workflow_documentation(
                workflow=wf,
                md_output_path=md_path,
                diagram_output_path=diagram_path,
            )

            self.assertTrue(os.path.exists(md_path))

            with open(md_path, encoding="utf-8") as f:
                content = f.read()

            self.assertIn("# 🕹️ Workflow:", content)
            self.assertIn("⚙️ Workflow Configuration", content)
            self.assertIn("📝 Workflow Input", content)
            self.assertIn("# 👾 Nodes:", content)
            self.assertIn("## 🖼️ Nodes Diagram", content)
            self.assertIn("Node 1# - A-test", content)
            self.assertIn("Node 2# - B-test", content)


