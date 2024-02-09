import typing

import numpy as np

import hpotk
from ._api import IndexedOntologyGraph, NODE


class StaticCsrArray:

    def __init__(self, indptr: typing.Sequence[int],
                 data: typing.Sequence[int]):
        self._indptr = np.array(indptr)
        self._data = np.array(data)
        self._max_row = len(self._indptr)

    def outgoing_nodes(self, row: int) -> typing.Sequence[int]:
        if row < 0 or self._max_row < row:
            raise ValueError(f'No such row {row}')

        start = self._indptr[row]
        end = self._indptr[row + 1]

        # TODO: maybe we can test if start==end and return a tuple if yes
        return self._data[start: end]


class CsrData:

    def __init__(self, children: StaticCsrArray,
                 parents: StaticCsrArray):
        self._children = children
        self._parents = parents

    @property
    def children(self) -> StaticCsrArray:
        return self._children

    @property
    def parents(self) -> StaticCsrArray:
        return self._parents


class CsrIndexedOntologyGraph(IndexedOntologyGraph):

    def __init__(self, root: int,
                 nodes: typing.Sequence[NODE],
                 csr_data: CsrData):
        self._root = hpotk.util.validate_instance(root, int, 'root')
        self._nodes = np.array(nodes)
        self._node_to_idx = {node: i for i, node in enumerate(self._nodes)}
        self._csr_data = hpotk.util.validate_instance(csr_data, CsrData, 'csr_data')

    @property
    def root_idx(self) -> int:
        return self._root

    def get_children_idx(self, source: int) -> typing.Sequence[int]:
        return self._csr_data.children.outgoing_nodes(source)

    def get_descendant_idx(self, source: int) -> typing.Iterator[int]:
        return self._traverse_graph(source, self.get_children_idx)

    def get_parents_idx(self, source: int) -> typing.Sequence[int]:
        return self._csr_data.parents.outgoing_nodes(source)

    def get_ancestor_idx(self, source: int) -> typing.Iterator[int]:
        return self._traverse_graph(source, self.get_parents_idx)

    def idx_to_node(self, idx: int) -> NODE:
        return self._nodes[idx]

    def node_to_idx(self, node: NODE) -> typing.Optional[int]:
        try:
            return self._node_to_idx[node]
        except KeyError:
            return None

    def __iter__(self) -> typing.Iterator[NODE]:
        return iter(self._nodes)

    @staticmethod
    def _traverse_graph(source: int,
                        supplier: typing.Callable[[int], typing.Sequence[int]]) -> typing.Generator[int, None, None]:
        seen = set()
        buffer = []

        for idx in supplier(source):
            seen.add(idx)
            buffer.append(idx)

        while buffer:
            current = buffer.pop()
            for idx in supplier(current):
                if idx not in seen:
                    seen.add(idx)
                    buffer.append(idx)

            yield current

    def __repr__(self):
        return f"CsrIndexedOntologyGraph(root={self.idx_to_node(self._root)}, n_nodes={len(self._nodes)})"
