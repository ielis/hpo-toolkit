import typing

import numpy as np

from hpotk.graph import OntologyGraph, GraphAware
from hpotk.model import TermId, Identified

from ._api import TermIdSorting


class Node(Identified):
    # Private API

    @staticmethod
    def merge_nodes(identifier, left, right):
        return Node(identifier, tag=False, left=left, right=right)

    @staticmethod
    def make_tagged_node(identifier: TermId):
        return Node(identifier=identifier, tag=True)

    def __init__(self, identifier: TermId,
                 tag: bool,
                 left=None,
                 right=None):
        self._id = identifier
        self._is_tagged = tag
        self._left = left
        self._right = right

    @property
    def identifier(self) -> TermId:
        return self._id

    @property
    def is_tagged(self) -> bool:
        return self._is_tagged

    @property
    def left(self):
        return self._left

    @property
    def right(self):
        return self._right

    def __repr__(self):
        return (f"Node(identifier={self._id}, "
                f"is_tagged={self._is_tagged}, "
                f"left={self._left}, "
                f"right={self._right})")


class HierarchicalSimilaritySorting(TermIdSorting):
    """
    `HierarchicalSimilaritySorting` uses hierarchical clustering to sort the term IDs.
    The clustering uses Resnik term similarity to assess term similarity.

    Notes:

    - Does *not* maintain order if the input is already sorted.

    :param hpo: HPO ontology graph or a graph aware instance.
    :param ic_source: a callable for getting the information content (IC) as a `float` for a term ID.
    """

    def __init__(self, hpo: typing.Union[OntologyGraph, GraphAware],
                 ic_source: typing.Callable[[TermId], float]):
        if isinstance(hpo, OntologyGraph):
            self._hpo = hpo
        elif isinstance(hpo, GraphAware):
            self._hpo = hpo.graph
        else:
            raise ValueError(f'`hpo` must be an instance of `OntologyGraph` or `GraphAware` but was {type(hpo)}')
        self._ic_source = ic_source

    def argsort(self, term_ids: typing.Sequence[typing.Union[TermId, Identified]]) -> typing.Sequence[int]:
        if len(term_ids) == 0:
            raise ValueError(f'Term ID sequence must not be empty!')

        term_ids = tuple(self._to_term_id(item) for item in term_ids)
        nodes = list(Node.make_tagged_node(tid) for tid in term_ids)

        node = self._hierarchical_cluster(nodes)

        ordered = []
        self._inorder_walk(node, ordered)

        return self._find_indices(term_ids, ordered)

    def _hierarchical_cluster(self, nodes: typing.MutableSequence[Node]) -> Node:
        while len(nodes) > 1:
            n_nodes = len(nodes)
            ics = np.zeros(shape=(n_nodes, n_nodes))
            micas = np.empty(shape=(n_nodes, n_nodes), dtype=object)

            for row in range(0, n_nodes):
                for col in range(row, n_nodes):
                    if row == col:
                        # No self-similarity!
                        continue
                    ic, mica = self._get_ic_and_mica(nodes[row], nodes[col])
                    ics[row, col] = ic
                    ics[col, row] = ic
                    micas[row, col] = mica
                    micas[col, row] = mica

            max_row, max_col = np.unravel_index(np.argmax(ics, axis=None), ics.shape)
            ic_mica = ics[max_row, max_col]

            if ic_mica <= 5E-6:
                # IC is close to zero - should happen when there is no good match left for the remaining nodes,
                # and we need to cluster the rest kind of arbitrarily
                a = nodes.pop()
                b = nodes.pop()
                _, mica = self._get_ic_and_mica(a, b)
                node = Node.merge_nodes(mica, a, b)
            else:
                # Let's cluster together the most similar term id pair.
                max_term_id = micas[max_row, max_col]
                a = nodes.pop(max(max_row, max_col))
                b = nodes.pop(min(max_row, max_col))
                node = Node.merge_nodes(max_term_id, a, b)

            nodes.append(node)

        return nodes[0]

    def _inorder_walk(self, node: Node,
                      collector: typing.MutableSequence[TermId]):
        # Traverse the node and collect the tagged nodes in the collector.
        if node.left is not None:
            self._inorder_walk(node.left, collector)
        if node.is_tagged:
            collector.append(node.identifier)
        if node.right is not None:
            self._inorder_walk(node.right, collector)

    def _get_ic_and_mica(self, a: typing.Union[TermId, Identified],
                         b: typing.Union[TermId, Identified]) -> typing.Tuple[float, TermId]:
        # Find the common ancestors of `a` and `b` and find the most informative common ancestor
        # along with its information content.
        a_anc = set(self._hpo.get_ancestors(a, include_source=True))
        b_anc = set(self._hpo.get_ancestors(b, include_source=True))
        common_ancestors = a_anc.intersection(b_anc)

        return max(
            map(lambda t: (self._ic_source(t), t), common_ancestors),
            key=lambda tup: tup[0],  # Order by similarity
            default=(0., None)
        )

    @staticmethod
    def _find_indices(source: typing.Sequence[TermId],
                      ordered: typing.Sequence[TermId]) -> typing.Sequence[int]:
        """
        Find indices that will sort `source` to the order of `ordered` sequence.
        """
        assert len(source) == len(ordered)

        return tuple(source.index(s) for s in ordered)

    @staticmethod
    def _to_term_id(item: typing.Union[TermId, Identified]) -> TermId:
        if isinstance(item, TermId):
            return item
        elif isinstance(item, Identified):
            return item.identifier
        else:
            raise ValueError(f'Item {item} is not `TermId` or `Identified` but it is {type(item)}')
