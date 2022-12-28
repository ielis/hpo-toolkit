import abc
import logging
import typing

from hpotk.model import TermId
from ._api import OntologyGraph, NODE, OWL_THING
from ._csr_graph import SimpleCsrOntologyGraph
from .csr import CsrMatrixBuilder, ImmutableCsrMatrix

import numpy as np
import numpy.typing as npt

# A newtype for stronger typing. We use these in `GraphFactory` below.
DirectedEdge = typing.Tuple[TermId, TermId]
GRAPH = typing.TypeVar('GRAPH', bound=OntologyGraph)


class GraphFactory(typing.Generic[GRAPH], metaclass=abc.ABCMeta):
    """
    Graph factory creates a graph from a list of `TermId` pairs
    """

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    @abc.abstractmethod
    def create_graph(self, edge_list: typing.Sequence[DirectedEdge]) -> GRAPH:
        """
        Create graph from edge list.
        :param edge_list: a sequence of `DirectedEdge`s where the first item is the source
                          and the second item is the destination
        :return: the graph
        """
        pass

# TODO - remove networkx code!
# class NxGraphFactory(GraphFactory[NxOntologyGraph]):
#
#     def create_graph(self, edge_list: typing.Sequence[DirectedEdge]) -> NxOntologyGraph:
#         # Find root node
#         root, edge_list = _phenol_find_root(edge_list)
#         # Prepare the networkx graph
#         g: nx.DiGraph = nx.from_edgelist(edge_list, create_using=nx.DiGraph)
#         # Assemble the wrapper
#         return NxOntologyGraph(root, g)


class CsrGraphFactory(GraphFactory[SimpleCsrOntologyGraph]):
    """
    A factory for creating `OntologyGraph` that is backed by a compressed sparse row (CSR) connectivity matrix.
    """

    def create_graph(self, edge_list: typing.Sequence[DirectedEdge]) -> SimpleCsrOntologyGraph:
        # Find root node
        root, edge_list = _phenol_find_root(edge_list)

        # Prepare node list
        nodes: npt.ArrayLike = _extract_nodes(edge_list)

        # Build connectivity matrix
        node_to_idx = {node: idx for idx, node in enumerate(nodes)}
        builder = CsrMatrixBuilder(shape=(len(nodes), len(nodes)))
        for edge in edge_list:
            src_idx = node_to_idx[edge[0]]
            dest_idx = node_to_idx[edge[1]]
            builder[src_idx, dest_idx] = SimpleCsrOntologyGraph.PARENT_RELATIONSHIP_CODE
            builder[dest_idx, src_idx] = SimpleCsrOntologyGraph.CHILD_RELATIONSHIP_CODE

        connectivity_matrix = ImmutableCsrMatrix(builder.row,
                                                 builder.col,
                                                 builder.data,
                                                 builder.shape,
                                                 dtype=int)
        # Assemble the ontology
        return SimpleCsrOntologyGraph(root, nodes, connectivity_matrix)


def _extract_and_sort_nodes(edge_list: typing.Sequence[DirectedEdge]) -> npt.ArrayLike:
    return np.sort(_extract_nodes(edge_list))


def _extract_nodes(edge_list: typing.Sequence[DirectedEdge]) -> npt.ArrayLike:
    nodes: typing.Set[TermId] = set()
    for edge in edge_list:
        nodes.add(edge[0])
        nodes.add(edge[1])
    return np.array(list(nodes), dtype=object)


def _phenol_find_root(edge_list: typing.Sequence[DirectedEdge]) -> typing.Tuple[NODE, typing.Sequence[DirectedEdge]]:
    """
    Find an ontology root candidate - the term that is parent of all elements using `DirectedEdge` that represents
    `src` -> `is_a` -> `dst` relationship.

    The method finds `TermId`s with no parents. There are 3 situations that can happen:
    - no `TermId` with no parents are found - we throw an error
    - one `TermId` with no parents is found, this is the root candidate
    - two or more `TermId`s with no parents are found, we add `OWL_THING` as the root term.
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
        raise ValueError(f'No root candidate found')
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
