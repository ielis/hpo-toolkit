# TODO - remove networkx code!
# import typing
# import networkx as nx
#
# from ._api import OntologyGraph, NODE
#
#
# class NxOntologyGraph(OntologyGraph):
#
#     def __init__(self, root: NODE, graph: nx.DiGraph):
#         self._root = root
#         self._graph: nx.DiGraph = graph
#
#     @property
#     def root(self) -> NODE:
#         return self._root
#
#     def get_children(self, source: NODE) -> typing.Iterator[NODE]:
#         return self._graph.predecessors(source)
#
#     def get_parents(self, source: NODE) -> typing.Iterator[NODE]:
#         return self._graph.successors(source)
#
#     def __contains__(self, item: NODE) -> bool:
#         return self._graph.has_node(item)
#
#     def __iter__(self) -> typing.Iterator[NODE]:
#         return self._graph.nodes
