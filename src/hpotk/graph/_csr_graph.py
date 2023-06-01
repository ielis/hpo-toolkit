import abc
import bisect
import typing
import warnings
from collections import deque

import numpy as np

from hpotk.model import TermId, Identified
from hpotk.util import validate_instance
from ._api import OntologyGraph, NODE
from .csr import ImmutableCsrMatrix


class BaseCsrOntologyGraph(OntologyGraph, metaclass=abc.ABCMeta):
    CHILD_RELATIONSHIP_CODE = 1
    PARENT_RELATIONSHIP_CODE = -1

    def __init__(self, root: NODE,
                 nodes: np.ndarray,
                 adjacency_matrix: ImmutableCsrMatrix):
        self._root = validate_instance(root, TermId, 'root')
        self._nodes = validate_instance(nodes, np.ndarray, 'nodes')
        self._adjacency_matrix = validate_instance(adjacency_matrix, ImmutableCsrMatrix, 'adjacency_matrix')

    @property
    def root(self) -> NODE:
        return self._root

    def get_children(self, source: typing.Union[str, NODE, Identified],
                     include_source: bool = False) -> typing.Iterable[NODE]:
        # In other words, find a row in the CSR corresponding to the `source`
        # and retrieve the columns to which the `source` is the PARENT.
        return map(self._get_node_for_idx,
                   self._get_node_indices_with_relationship(source,
                                                            BaseCsrOntologyGraph.PARENT_RELATIONSHIP_CODE,
                                                            include_source))

    def get_descendants(self, source: typing.Union[str, NODE, Identified],
                        include_source: bool = False) -> typing.Iterable[NODE]:
        # See `self.get_children()` for explanation of `BaseCsrOntologyGraph.PARENT_RELATIONSHIP_CODE`.
        return map(self._get_node_for_idx,
                   self._traverse_graph(source,
                                        BaseCsrOntologyGraph.PARENT_RELATIONSHIP_CODE,
                                        include_source))

    def get_parents(self, source: typing.Union[str, NODE, Identified],
                    include_source: bool = False) -> typing.Iterable[NODE]:
        # In other words, find a row in the CSR corresponding to the `source`
        # and retrieve the columns to which the `source` is the CHILD.
        return map(self._get_node_for_idx,
                   self._get_node_indices_with_relationship(source,
                                                            BaseCsrOntologyGraph.CHILD_RELATIONSHIP_CODE,
                                                            include_source))

    def get_ancestors(self, source: typing.Union[str, NODE, Identified],
                      include_source: bool = False) -> typing.Iterable[NODE]:
        # See `self.get_parents()` for explanation of `BaseCsrOntologyGraph.CHILD_RELATIONSHIP_CODE`.
        return map(self._get_node_for_idx,
                   self._traverse_graph(source,
                                        BaseCsrOntologyGraph.CHILD_RELATIONSHIP_CODE,
                                        include_source))

    def is_leaf(self, node: typing.Union[str, NODE, Identified]) -> bool:
        for _ in self._get_node_indices_with_relationship(node, BaseCsrOntologyGraph.PARENT_RELATIONSHIP_CODE, False):
            return False
        return True

    def __contains__(self, item: NODE) -> bool:
        return self._get_idx_for_node(item) is not None

    def __iter__(self) -> typing.Iterator[NODE]:
        return iter(self._nodes)

    def _traverse_graph(self, source: typing.Union[str, NODE, Identified],
                        relationship,
                        include_source: bool) -> typing.Generator[int, None, None]:
        source: TermId = self._map_to_term_id(source)
        seen: set[int] = set()
        buffer: typing.Deque[int] = deque()

        # Init
        for idx in self._get_node_indices_with_relationship(source, relationship, include_source):
            seen.add(idx)
            buffer.append(idx)

        # Loop
        while buffer:
            current = buffer.popleft()
            for idx in self._get_cols_with_relationship(current, relationship):
                if idx not in seen:
                    seen.add(idx)
                    buffer.append(idx)

            yield current

    def _get_node_indices_with_relationship(self, source: typing.Union[str, NODE, Identified],
                                            relationship,
                                            include_source: bool) -> typing.Generator[int, None, None]:
        source: TermId = self._map_to_term_id(source)
        row_idx = self._get_idx_for_node(source)
        if include_source:
            yield row_idx

        for idx in self._get_cols_with_relationship(row_idx, relationship):
            yield idx

    def _get_cols_with_relationship(self, idx: typing.Optional[int],
                                    relationship) -> typing.Generator[int, None, None]:
        if idx is None:
            return
        col_indices = self._adjacency_matrix.col_indices_of_val(idx, relationship)
        for col_idx in col_indices:
            yield int(col_idx)  # Numpy returns np.i64 but we need int

    @abc.abstractmethod
    def _get_idx_for_node(self, node: NODE) -> typing.Optional[int]:
        pass

    def _get_node_for_idx(self, idx: int) -> NODE:
        return self._nodes[idx]


class SimpleCsrOntologyGraph(BaseCsrOntologyGraph):
    """
    An implementation of :class:`OntologyGraph` that uses a :class:`dict` to map a NODE to adjacency matrix index.
    """

    def __init__(self, root: NODE,
                 nodes: np.ndarray,
                 adjacency_matrix: ImmutableCsrMatrix):
        super().__init__(root, nodes, adjacency_matrix)
        self._node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        warnings.warn('SimpleCsrOntologyGraph will be removed from the public API in v1.0.0',
                      DeprecationWarning, stacklevel=2)

    def _get_idx_for_node(self, node: NODE) -> typing.Optional[int]:
        return self._node_to_idx[node]


class BisectPoweredCsrOntologyGraph(BaseCsrOntologyGraph):
    """
    An implementation of :class:`OntologyGraph` that uses binary search to look up NODE index.
    """

    def __init__(self, root: NODE,
                 nodes: np.ndarray,
                 adjacency_matrix: ImmutableCsrMatrix,
                 skip_validation: bool = False):
        super().__init__(root, nodes, adjacency_matrix)
        if not skip_validation:
            # NOTE - the `nodes` array ABSOLUTELY MUST be a sorted.
            # Otherwise, the traversal functionality will not work!
            check_items_are_sorted(nodes)

    def _get_idx_for_node(self, node: NODE) -> typing.Optional[int]:
        idx = bisect.bisect_left(self._nodes, node)
        if idx != len(self._nodes) and self._nodes[idx] == node:
            return idx
        return None


def check_items_are_sorted(items: typing.Iterable[NODE]):
    """
    Check that items are sorted in ascending order according to their natural ordering.
    :param items: an iterable of items.
    :return: `None` if the items are sorted or raise :class:`ValueError` if the items is unsorted.
    """
    previous = None
    for i, node in enumerate(items):
        if previous and node < previous:
            raise ValueError(f'Unsorted sequence. Item #{i} ({node}) was less than #{i - 1} ({previous})')
        previous = node
