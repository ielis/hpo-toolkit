import abc

import typing

from hpotk.model import TermId

NODE = typing.TypeVar('NODE', bound=TermId)


class OntologyGraph(typing.Generic[NODE], metaclass=abc.ABCMeta):
    """
    A simple graph with one node type and one edge type.

    The graph is generic over a node type which must extend `hpotk.base.model.TermId`. The graph must not be empty
    """

    @property
    @abc.abstractmethod
    def root(self) -> NODE:
        pass

    @abc.abstractmethod
    def get_children(self, source: NODE) -> typing.Iterator[NODE]:
        pass

    @abc.abstractmethod
    def get_parents(self, source: NODE) -> typing.Iterator[NODE]:
        pass

    @abc.abstractmethod
    def __contains__(self, item: NODE) -> bool:
        pass

    @abc.abstractmethod
    def __iter__(self) -> typing.Iterator[NODE]:
        pass


class GraphAware(typing.Generic[NODE], metaclass=abc.ABCMeta):
    """
    Base class for entities that have an `OntologyGraph`.
    """

    @property
    @abc.abstractmethod
    def graph(self) -> OntologyGraph[NODE]:
        """
        :return: the ontology graph with nodes of a given type.
        """
        pass
