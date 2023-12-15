import abc
import typing
import warnings

import numpy as np

from hpotk.graph import OntologyGraph, GraphAware
from hpotk.model import TermId, Identified

from ._api import TermIdSorting


def to_term_id(item: typing.Union[TermId, Identified]) -> TermId:
    """
    Private utility method for converting the input into a `TermId`.
    """
    if isinstance(item, TermId):
        return item
    elif isinstance(item, Identified):
        return item.identifier
    else:
        raise ValueError(f'Item {item} is not `TermId` or `Identified` but it is {type(item)}')


def to_ontology_graph(hpo: typing.Union[GraphAware, OntologyGraph]) -> OntologyGraph:
    if isinstance(hpo, OntologyGraph):
        return hpo
    elif isinstance(hpo, GraphAware):
        return hpo.graph
    else:
        raise ValueError(f'`hpo` must be an instance of `OntologyGraph` or `GraphAware` but was {type(hpo)}')


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


class SimilarityMeasure(metaclass=abc.ABCMeta):
    # Private API

    @abc.abstractmethod
    def compute_similarity(self, left: typing.Union[TermId, Identified],
                           right: typing.Union[TermId, Identified]) -> typing.Tuple[float, TermId]:
        """
        Compute similarity of two term IDs along with the most specific node.

        :param left: an ontology node.
        :param right: other ontology node.
        :return: a tuple with node similarity and the most specific node
        """
        pass


class IcSimilarityMeasure(SimilarityMeasure):
    """
    `IcSimilarityMeasure` uses information content of the most informative common ancestor as the similarity measure
    and MICA as the most specific node.
    """
    # Private API

    def __init__(self, hpo: typing.Union[OntologyGraph, GraphAware],
                 ic_source: typing.Callable[[TermId], float]):
        self._hpo = to_ontology_graph(hpo)
        self._ic_source = ic_source

    def compute_similarity(self, left: typing.Union[TermId, Identified],
                           right: typing.Union[TermId, Identified]) -> typing.Tuple[float, TermId]:

        # Find the common ancestors of `a` and `b` and find the most informative common ancestor
        # along with its information content.
        a_anc = set(self._hpo.get_ancestors(left, include_source=True))
        b_anc = set(self._hpo.get_ancestors(right, include_source=True))
        common_ancestors = a_anc.intersection(b_anc)

        return max(
            map(lambda t: (self._ic_source(t), t), common_ancestors),
            key=lambda tup: tup[0],  # Order by similarity
            default=(0., None)
        )


class EdgeSimilarityMeasure(SimilarityMeasure):
    """
    `EdgeSimilarityMeasure` uses the reciprocal of the edge distance as a similarity and most specific common ancestor
    as the most specific node.

    Note, if two paths exist between the query nodes through two separate nodes that also happen to be the most specific
    common ancestors, then one of them is chosen at random.
    """
    # Private API

    def __init__(self, hpo: typing.Union[OntologyGraph, GraphAware]):
        self._hpo = to_ontology_graph(hpo)

    def compute_similarity(self, left: typing.Union[TermId, Identified],
                           right: typing.Union[TermId, Identified]) -> typing.Tuple[float, TermId]:
        dist, node = self.calculate_edge_distance(left, right)

        sim = 1 if dist == 0 else 1 / dist

        return sim, node

    def calculate_edge_distance(self, left: TermId, right: TermId) -> typing.Tuple[int, TermId]:
        left, right = to_term_id(left), to_term_id(right)
        if left == right:
            # Distance to self is `0`.
            return 0, left

        left_dist = self._get_ancestor_distances(left)
        right_dist = self._get_ancestor_distances(right)

        return self._find_minimum_distance(left_dist, right_dist)

    def _get_ancestor_distances(self, src: TermId) -> typing.Mapping[TermId, int]:
        distances = {}
        seen = set()

        stack = [(0, src)]
        while stack:
            distance, term_id = stack.pop()

            current = distance + 1
            for parent in self._hpo.get_parents(term_id):
                if parent not in seen:
                    stack.append((current, parent))
                seen.add(parent)

            if term_id in distances:
                # We must keep the shortest distance
                distances[term_id] = min(distances[term_id], distance)
            else:
                distances[term_id] = distance

        return distances

    @staticmethod
    def _find_minimum_distance(left_dist: typing.Mapping[TermId, int],
                               right_dist: typing.Mapping[TermId, int]) -> typing.Tuple[int, TermId]:
        dist = None
        ancestor = None
        for shared in left_dist.keys() & right_dist.keys():
            current = left_dist[shared] + right_dist[shared]
            if dist is None:
                dist = current
                ancestor = shared
            else:
                if current < dist:
                    # Note: we do not update if current = dist. In result, I suspect that the algorithm is not "stable"
                    # in terms of sorting.
                    dist = current
                    ancestor = shared

        return dist, ancestor


class HierarchicalSorting(TermIdSorting, metaclass=abc.ABCMeta):
    """
    `HierarchicalSorting` implements the hierarchical clustering functionality using
    given similarity measure.
    """
    # Private API

    def __init__(self, hpo: typing.Union[OntologyGraph, GraphAware],
                 sim_measure: SimilarityMeasure,
                 epsilon: float = 5e-10):
        self._hpo = to_ontology_graph(hpo)
        self._sim_measure = sim_measure
        self._epsilon = epsilon

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
            sims = np.zeros(shape=(n_nodes, n_nodes))
            ancestors = np.empty(shape=(n_nodes, n_nodes), dtype=object)

            for row in range(0, n_nodes):
                for col in range(row + 1, n_nodes):
                    ic, sim = self._sim_measure.compute_similarity(nodes[row], nodes[col])
                    sims[row, col] = ic
                    sims[col, row] = ic
                    ancestors[row, col] = sim
                    ancestors[col, row] = sim

            max_row, max_col = np.unravel_index(np.argmax(sims, axis=None), sims.shape)
            sim_anc = sims[max_row, max_col]

            if sim_anc <= self._epsilon:
                # sim is close to zero - should happen when there is no good match left for the remaining nodes,
                # and we need to cluster the rest kind of arbitrarily
                a = nodes.pop()
                b = nodes.pop()
                _, sim = self._sim_measure.compute_similarity(a, b)
                node = Node.merge_nodes(sim, a, b)
            else:
                # Let's cluster together the most similar term id pair.
                max_term_id = ancestors[max_row, max_col]
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

    @staticmethod
    def _to_term_id(item: typing.Union[TermId, Identified]) -> TermId:
        if isinstance(item, TermId):
            return item
        elif isinstance(item, Identified):
            return item.identifier
        else:
            raise ValueError(f'Item {item} is not `TermId` or `Identified` but it is {type(item)}')

    @staticmethod
    def _find_indices(source: typing.Sequence[TermId],
                      ordered: typing.Sequence[TermId]) -> typing.Sequence[int]:
        """
        Find indices that will sort `source` to the order of `ordered` sequence.
        """
        assert len(source) == len(ordered)

        return tuple(source.index(s) for s in ordered)


class HierarchicalEdgeTermIdSorting(HierarchicalSorting):
    """
    `HierarchicalEdgeTermIdSorting` uses hierarchical clustering to sort the term IDs.
    The clustering uses edge distance as a proxy to the term similarity.

    Notes:

    - Does *not* maintain order if the input is already sorted.

    :param hpo: HPO ontology graph or a graph aware instance.
    """

    def __init__(self, hpo: typing.Union[OntologyGraph, GraphAware]):
        super().__init__(hpo, EdgeSimilarityMeasure(hpo))


class HierarchicalIcTermIdSorting(HierarchicalSorting):
    """
    `HierarchicalIcTermIdSorting` uses hierarchical clustering to sort the term IDs.
    The clustering uses Resnik term similarity to assess term similarity.

    Notes:

    - Does *not* maintain order if the input is already sorted.

    :param hpo: HPO ontology graph or a graph aware instance.
    :param ic_source: a callable for getting the information content (IC) as a `float` for a term ID.
    """

    def __init__(self, hpo: typing.Union[OntologyGraph, GraphAware],
                 ic_source: typing.Callable[[TermId], float]):
        super().__init__(hpo, IcSimilarityMeasure(hpo, ic_source))

    def argsort(self, term_ids: typing.Sequence[typing.Union[TermId, Identified]]) -> typing.Sequence[int]:
        if len(term_ids) == 0:
            raise ValueError(f'Term ID sequence must not be empty!')

        term_ids = tuple(to_term_id(item) for item in term_ids)
        nodes = list(Node.make_tagged_node(tid) for tid in term_ids)

        node = self._hierarchical_cluster(nodes)

        ordered = []
        self._inorder_walk(node, ordered)

        return self._find_indices(term_ids, ordered)


class HierarchicalSimilaritySorting(HierarchicalIcTermIdSorting):
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
        super().__init__(hpo, ic_source)
        warnings.warn("HierarchicalSimilaritySorting was deprecated and will be remove in v1.0.0. "
                      "Use HierarchicalIcTermIdSorting instead", DeprecationWarning, stacklevel=2)
