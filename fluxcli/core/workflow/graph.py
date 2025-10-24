from collections.abc import Callable
from graphlib import CycleError, TopologicalSorter

from pydantic import BaseModel, Field

from fluxcli.core.node.node import Node
from fluxcli.core.status import StatusCodes


class Edge(BaseModel):
    source: str = Field(...)
    destination: str = Field(...)
    condition: Callable[[], bool] | None = None
    condition_passed: bool | None = None

    def evaluate_condition(self) -> bool:
        self.condition_passed = True if self.condition is None else bool(self.condition())
        return self.condition_passed


class WorkflowGraph(BaseModel):
    nodes: dict[str, Node] = Field(default_factory=dict)
    edges: list[Edge] = Field(default_factory=list)

    def get_parents(self, node: Node) -> list[Node]:
        return [self.nodes[edge.source] for edge in self.edges if edge.destination == node.name]

    def get_children(self, node: Node) -> list[Node]:
        return [self.nodes[edge.destination] for edge in self.edges if edge.source == node.name]

    def add_node(self, node: Node) -> None:
        if node.name in self.nodes:
            raise ValueError(f"Node '{node.name}' already exists.")
        self.nodes[node.name] = node

    def add_edge(self, source_node: Node, dest_node: Node) -> Edge:
        self._validate_nodes(source_node, dest_node)
        self._validate_no_duplicate_edge(source_node, dest_node)
        edge = Edge(source=source_node.name, destination=dest_node.name)
        self._validate_acyclic(edge)
        self.edges.append(edge)
        return edge

    def add_conditional_edge(self, source_node: Node, dest_node: Node, condition: Callable[[], bool]) -> Edge:
        self._validate_nodes(source_node, dest_node)
        self._validate_no_duplicate_edge(source_node, dest_node)
        edge = Edge(source=source_node.name, destination=dest_node.name, condition=condition)
        self._validate_acyclic(edge)
        self.edges.append(edge)
        return edge

    def add_edge_if_source_completed(self, source_node: Node, dest_node: Node) -> Edge:
        self._validate_nodes(source_node, dest_node)
        self._validate_no_duplicate_edge(source_node, dest_node)

        def condition() -> bool:
            return source_node.attempt > 0 and source_node.last_execution.status == StatusCodes.COMPLETED

        edge = Edge(source=source_node.name, destination=dest_node.name, condition=condition)
        self._validate_acyclic(edge)
        self.edges.append(edge)
        return edge

    def get_edge(self, source: Node, destination: Node) -> Edge | None:
        return next(
            (edge for edge in self.edges if edge.source == source.name and edge.destination == destination.name),
            None,
        )

    def _validate_nodes(self, source_node: Node, dest_node: Node) -> None:
        if source_node.name not in self.nodes or dest_node.name not in self.nodes:
            raise ValueError("Both source and destination nodes must exist in the graph.")
        if source_node.name == dest_node.name:
            raise ValueError("Cannot create self-loop edges.")

    def _validate_acyclic(self, new_edge: Edge) -> None:
        sorter = TopologicalSorter()

        for e in self.edges:
            sorter.add(e.destination, e.source)

        sorter.add(new_edge.destination, new_edge.source)

        try:
            list(sorter.static_order())
        except CycleError:
            raise ValueError(f"edge {new_edge.source} → {new_edge.destination} creates a cycle.")

    def _edge_exists(self, source: str, destination: str) -> bool:
        return any(e.source == source and e.destination == destination for e in self.edges)

    def _validate_no_duplicate_edge(self, source_node: Node, dest_node: Node) -> None:
        if self._edge_exists(source_node.name, dest_node.name):
            raise ValueError(f"Edge '{source_node.name}' → '{dest_node.name}' already exists.")

    def can_node_run(self, node: Node, completed: set[Node]) -> bool:
        if node.name in completed:
            return False

        parents = self.get_parents(node)

        if not parents:
            return True

        completed_names = {n.name for n in completed}

        for parent in parents:
            if parent.name not in completed_names:
                return False

            edge = self.get_edge(parent, node)
            if edge is not None and edge.condition is not None:
                if not edge.condition():
                    return False

        return True

    # TODO: Add a method to run a node
    # TODO: Add a method to get the next runnable nodes
