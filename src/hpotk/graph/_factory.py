import abc
import bisect
import logging
import typing
import warnings
from collections import defaultdict

import numpy as np

from hpotk.model import TermId
from ._api import OntologyGraph, IndexedOntologyGraph, NODE, OWL_THING
from ._csr_graph import SimpleCsrOntologyGraph, BisectPoweredCsrOntologyGraph
from ._csr_idx_graph import StaticCsrArray, CsrData, CsrIndexedOntologyGraph
from .csr import CsrMatrixBuilder, ImmutableCsrMatrix

# A newtype for stronger typing. We use these in `GraphFactory` below.
DirectedEdge = typing.Tuple[TermId, TermId]
GRAPH = typing.TypeVar('GRAPH', bound=OntologyGraph)


class GraphFactory(typing.Generic[GRAPH], metaclass=abc.ABCMeta):
    """
    Graph factory creates a graph from a list of `TermId` pairs.
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def create_graph(self, edge_list: typing.Sequence[DirectedEdge]) -> GRAPH:
        """
        Create graph from edge list.

        :param edge_list: a sequence of directed edges - tuples where the first item is the source
          and the second item is the destination.
        :return: the graph
        """
        pass


class AbstractCsrGraphFactory(GraphFactory[OntologyGraph], metaclass=abc.ABCMeta):

    def create_graph(self, edge_list: typing.Sequence[DirectedEdge]) -> OntologyGraph:
        # Find root node
        self._logger.debug('Creating ontology graph from %d edges', len(edge_list))
        root, edge_list = _phenol_find_root(edge_list)
        self._logger.debug('Found root %s', root.value)

        # Prepare node list. We MUST sort the list, otherwise building of the IncrementalCsrMatrix won't work.
        nodes = get_array_of_unique_and_sorted_nodes(edge_list)
        self._logger.debug('Extracted %d nodes', len(nodes))

        # Build the adjacency matrix
        self._logger.debug('Building sparse adjacency matrix')
        cm = self._build_adjacency_matrix(nodes, edge_list)
        # Assemble the ontology
        self._logger.debug('Finalizing the ontology graph')
        return BisectPoweredCsrOntologyGraph(root, nodes, cm)

    @abc.abstractmethod
    def _build_adjacency_matrix(self, nodes: typing.Sequence[TermId],
                                edges: typing.Sequence[DirectedEdge]) -> ImmutableCsrMatrix:
        pass


class CsrGraphFactory(AbstractCsrGraphFactory):
    """
    A factory for creating `OntologyGraph` that is backed by a compressed sparse row (CSR) connectivity matrix.

    .. deprecated::
      Use :class:`hpotk.graph.IncrementalCsrGraphFactory` instead.
    """

    def __init__(self):
        # REMOVE(v1.0.0)
        warnings.warn('CsrGraphFactory was deprecated and will be removed in v1.0.0', DeprecationWarning, stacklevel=2)
        super().__init__()

    def _build_adjacency_matrix(self, nodes: typing.Sequence[TermId],
                                edges: typing.Sequence[DirectedEdge]):
        node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        builder = CsrMatrixBuilder(shape=(len(nodes), len(nodes)))
        for edge in edges:
            src_idx = node_to_idx[edge[0]]
            dest_idx = node_to_idx[edge[1]]
            builder[src_idx, dest_idx] = SimpleCsrOntologyGraph.CHILD_RELATIONSHIP_CODE
            builder[dest_idx, src_idx] = SimpleCsrOntologyGraph.PARENT_RELATIONSHIP_CODE
        return ImmutableCsrMatrix(builder.row,
                                  builder.col,
                                  builder.data,
                                  builder.shape,
                                  dtype=int)


class CsrIndexedGraphFactory(GraphFactory[IndexedOntologyGraph]):
    """
    `CsrIndexedGraphFactory` builds an :class:`IndexedOntologyGraph` that is backed by two CSR arrays for storing
    the parent and child nodes of an ontology graph node.
    """

    def __init__(self):
        super().__init__()

    def create_graph(self, edge_list: typing.Sequence[DirectedEdge]) -> IndexedOntologyGraph[TermId]:
        # Find root node
        self._logger.debug('Creating ontology graph from %d edges', len(edge_list))
        root, edge_list = _phenol_find_root(edge_list)
        self._logger.debug('Found root %s', root.value)

        # Prepare node list. We MUST sort the list, otherwise building of the IncrementalCsrMatrix won't work.
        nodes = get_array_of_unique_and_sorted_nodes(edge_list)
        self._logger.debug('Extracted %d nodes', len(nodes))

        root_idx = self._find_root_idx(root, nodes)
        csr_data = self._build_csr_data(nodes, edge_list)

        return CsrIndexedOntologyGraph(root_idx, nodes, csr_data)

    @staticmethod
    def _find_root_idx(root: NODE,
                       nodes: typing.Sequence[NODE]) -> int:
        # Simple linear search for now
        for i, node in enumerate(nodes):
            if node == root:
                return i

        raise ValueError(f'Did not find root {root} in the nodes')

    def _build_csr_data(self, nodes: np.ndarray,
                        edges: typing.Sequence[DirectedEdge]) -> CsrData:
        adjacent_edges = self._find_adjacent_edges(nodes, edges)

        parent_indptr, parents = [0], []
        child_indptr, children = [0], []

        for row_idx, source in enumerate(nodes):
            adjacent = adjacent_edges.get(row_idx, ())

            for edge in adjacent:
                target_is_child = source == edge[1]  # edge[1] is the object
                target = edge[0] if target_is_child else edge[1]
                idx = _index_of_using_binary_search(nodes, target)
                if target_is_child:
                    children.append(idx)
                else:
                    parents.append(idx)

            parent_indptr.append(len(parents))
            child_indptr.append(len(children))

        parents = StaticCsrArray(parent_indptr, parents)
        children = StaticCsrArray(child_indptr, children)

        return CsrData(children=children, parents=parents)

    @staticmethod
    def _find_adjacent_edges(nodes: np.ndarray,
                             edges: typing.Sequence[DirectedEdge]) -> typing.Mapping[int, typing.Sequence[DirectedEdge]]:
        data = defaultdict(list)

        last_sub = None
        last_sub_idx = -1

        for edge in edges:
            sub = edge[0]
            if sub == last_sub:
                sub_idx = last_sub_idx
            else:
                last_sub = sub
                sub_idx = _index_of_using_binary_search(nodes, sub)
                last_sub_idx = sub_idx

            obj = edge[1]
            obj_idx = _index_of_using_binary_search(nodes, obj)

            data[sub_idx].append(edge)
            data[obj_idx].append(edge)

        return data


def get_array_of_unique_and_sorted_nodes(edge_list: typing.Sequence[DirectedEdge]) -> np.ndarray:
    edges = np.array(edge_list)
    return np.unique(edges)


def get_list_of_unique_nodes(edge_list: typing.Sequence[DirectedEdge]):
    return list(get_unique_nodes(edge_list))


def get_unique_nodes(edge_list: typing.Sequence[DirectedEdge]) -> typing.Collection[TermId]:
    nodes: typing.Set[TermId] = set()
    for edge in edge_list:
        nodes.add(edge[0])
        nodes.add(edge[1])
    return nodes


def _phenol_find_root(edge_list: typing.Sequence[DirectedEdge]) -> typing.Tuple[NODE, typing.Sequence[DirectedEdge]]:
    """
    Find an ontology root candidate - the term that is parent of all elements using `DirectedEdge` that represents
    `src` -> `is_a` -> `dst` relationship.

    The method finds term IDs with no parents. There are 3 situations that can happen:
    - no term ID with no parents are found - we throw an error
    - one term ID with no parents is found, this is the root candidate
    - two or more term IDs with no parents are found, we add `OWL_THING` as the root term.
    :param edge_list:
    :return: a tuple with the root and possibly updated edge_list
    """
    root_candidate_set: typing.Set[TermId] = set()
    remove_mark_set: typing.Set[TermId] = set()
    for edge in edge_list:
        root_candidate_set.add(edge[1])
        remove_mark_set.add(edge[0])

    candidates = root_candidate_set.difference(remove_mark_set)
    if len(candidates) == 0:
        raise ValueError('No root candidate found')
    if len(candidates) == 1:
        return candidates.pop(), edge_list
    else:
        # No single root candidate, so create a new one and add it into the nodes and edges
        # As per suggestion https://github.com/monarch-initiative/phenol/issues/163#issuecomment-452880405
        # We'll use owl:Thing instead of ID:0000000 so as not to potentially conflict with an existing term id.
        # TODO - we need tests!
        edge_list_copy = [val for val in edge_list]
        for candidate in candidates:
            edge = (candidate, OWL_THING)
            edge_list_copy.append(edge)

        return OWL_THING, edge_list_copy


class IncrementalCsrGraphFactory(AbstractCsrGraphFactory):
    """
    The CSR graph factory that builds the `row`, `col` and `data` in an incremental fashion.
    """

    def _build_adjacency_matrix(self, nodes: typing.Sequence[TermId],
                                edges: typing.Sequence[DirectedEdge]):
        row, col, data = make_row_col_data(nodes, edges)
        shape = (len(nodes), len(nodes))
        return ImmutableCsrMatrix(row, col, data, shape, dtype=int)


def make_row_col_data(nodes: typing.Sequence[TermId],
                      edge_list: typing.Sequence[DirectedEdge]):
    row = [0]
    col = []
    data = []
    partitioned_edges = _partition_edges(nodes, edge_list)

    for row_idx, node in enumerate(nodes):
        relevant_edges = partitioned_edges[row_idx]

        for target, relationship_code in sorted(_preprocess_edges(node, relevant_edges),
                                                key=lambda e: e[0]):  # We sort by the TermId
            idx = _index_of_using_binary_search(nodes, target)
            col.append(idx)
            data.append(relationship_code)

        row.append(len(data))

    return row, col, data


def _partition_edges(nodes: typing.Sequence[TermId],
                     edge_list: typing.Sequence[DirectedEdge]) -> typing.Mapping[int, typing.Sequence[DirectedEdge]]:
    """
    Prepare a mapping from a node index to all edges that reference the node.

    :param nodes: a sequence of nodes.
    :param edge_list: a sequence of edges.
    :return: a mapping from a node index to a sequence of edges that reference the node.
    """
    data = defaultdict(list)
    last_src = None
    last_idx = None
    for edge in edge_list:
        src = edge[0]
        if src == last_src:
            #  leverage Let's save one binary search
            src_idx = last_idx
        else:
            last_src = src
            src_idx = _index_of_using_binary_search(nodes, src)
            last_idx = src_idx
        dest = edge[1]
        dest_idx = _index_of_using_binary_search(nodes, dest)

        if src_idx is not None:
            data[src_idx].append(edge)
        if dest_idx is not None:
            data[dest_idx].append(edge)

    return data


def _preprocess_edges(source: TermId,
                      relevant_edges: typing.Iterable[DirectedEdge]):
    """
    Get a generator for yielding tuples with a term_id and a relationship code for terms/nodes that have a relationship
    with the `source`.

    :param source: a term ID for which we are generating the CSR row.
    :param relevant_edges: a sequence of edges that reference the `source` term ID
    :return: a tuple with the node/term ID and the relationship to store in the graph.
    """
    for edge in relevant_edges:
        sub, obj = edge
        if source != sub and source == obj:
            # `source` is the object. Since we are getting `is_a` relationships, the current edge must represent
            # something `is_a` `source`, hence `source` is the parent.
            yield sub, SimpleCsrOntologyGraph.PARENT_RELATIONSHIP_CODE
        elif source != obj and source == sub:
            yield obj, SimpleCsrOntologyGraph.CHILD_RELATIONSHIP_CODE
        else:
            raise ValueError(f'source {source} must either be a subject or object of the edge {edge}')


def _index_of_using_binary_search(a: typing.Sequence[TermId], x: TermId) -> typing.Optional[int]:
    idx = bisect.bisect_left(a, x)
    if idx != len(a) and a[idx] == x:
        return idx
    return None
