import typing
import networkx as nx
from collections import deque

from ._api import OntologyGraph, NODE


class NxOntologyGraph(OntologyGraph):

    def __init__(self, graph: nx.DiGraph):
        self._graph: nx.DiGraph = graph
        candidate = self._find_root(graph)
        if not candidate:
            raise ValueError(f'Unable to find root term ID')
        self._root = candidate

    @property
    def root(self) -> NODE:
        return self._root

    def get_children(self, source: NODE) -> typing.Iterator[NODE]:
        return self._graph.predecessors(source)

    def get_parents(self, source: NODE) -> typing.Iterator[NODE]:
        return self._graph.successors(source)

    def __contains__(self, item: NODE) -> bool:
        return self._graph.has_node(item)

    def __iter__(self) -> typing.Iterator[NODE]:
        return self._graph.nodes

    @staticmethod
    def _find_root(graph: nx.DiGraph) -> typing.Optional[NODE]:
        """
        Find root of the `graph`.

        The strategy is simple and should work for HPO but may fail for ontologies with multiple roots (e.g. GO).
        We start with a random node and find its top-level ancestor. We return the ancestor or `None` if the graph
        has no nodes.

        :param graph: graph to work with
        :return:
        """
        # TODO - this is not a complete solution and it will fail for ontologies with multiple roots.
        #  Like in Phenol, we must implement adding an artificial root: owl:Thing.
        nodes = deque([])
        for node in graph.nodes():
            nodes.append(node)
            break

        node: typing.Optional[NODE] = None
        while nodes:
            node = nodes.popleft()
            for parent in graph.successors(node):
                nodes.append(parent)

        return node
