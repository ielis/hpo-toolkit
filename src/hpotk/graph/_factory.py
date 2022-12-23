import abc
import logging
import typing

from hpotk.model import TermId
from ._api import OntologyGraph
from ._csr import CsrOntologyGraph
from .nx import NxOntologyGraph

import networkx as nx

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


class NxGraphFactory(GraphFactory[NxOntologyGraph]):

    def create_graph(self, edge_list: typing.Sequence[DirectedEdge]) -> NxOntologyGraph:
        g: nx.DiGraph = nx.from_edgelist(edge_list, create_using=nx.DiGraph)
        return NxOntologyGraph(g)


class CsrGraphFactory(GraphFactory[CsrOntologyGraph]):
    """
    A factory for creating `OntologyGraph` that is backed by a compressed sparse row (CSR) connectivity matrix.
    """

    def create_graph(self, edge_list: typing.Sequence[DirectedEdge]) -> CsrOntologyGraph:
        # TODO - start here!
        raise NotImplemented('Not yet implemented')
