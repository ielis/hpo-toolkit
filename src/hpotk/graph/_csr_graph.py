import typing

from ._api import OntologyGraph, NODE
from .csr import ImmutableCsrMatrix


class SimpleCsrOntologyGraph(OntologyGraph):
    """
    Simple CSR ontology graph uses a dict to map a NODE to connectivity matrix index.
    """

    # TODO - try replacing `self._node_to_idx` with binary search.
    CHILD_RELATIONSHIP_CODE = 1
    PARENT_RELATIONSHIP_CODE = -1

    def __init__(self, root: NODE,
                 nodes: typing.Sequence[NODE],
                 connectivity_matrix: ImmutableCsrMatrix):
        self._root = root
        self._nodes = nodes
        self._node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        self._connectivity_matrix = connectivity_matrix

    @property
    def root(self) -> NODE:
        return self._root

    def get_children(self, source: NODE) -> typing.Iterator[NODE]:
        return self._get_nodes_with_relationship(source,
                                                 SimpleCsrOntologyGraph.CHILD_RELATIONSHIP_CODE)

    def get_parents(self, source: NODE) -> typing.Iterator[NODE]:
        return self._get_nodes_with_relationship(source,
                                                 SimpleCsrOntologyGraph.PARENT_RELATIONSHIP_CODE)

    def _get_nodes_with_relationship(self, source, relationship):
        node_idx = self._node_to_idx[source]
        child_idxs = self._connectivity_matrix.col_indices_of_val(node_idx, relationship)
        return self._nodes[child_idxs]

    def __contains__(self, item: NODE) -> bool:
        return item in self._node_to_idx

    def __iter__(self) -> typing.Iterator[NODE]:
        return iter(self._nodes)
