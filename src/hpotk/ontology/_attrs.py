import abc
import typing

from hpotk.model import TermId
from hpotk.graph import OntologyGraph

ID = typing.TypeVar('ID', bound=TermId)


class GraphAware(metaclass=abc.ABCMeta):
    """
    Base class for entities that have an `OntologyGraph`.
    """

    @property
    @abc.abstractmethod
    def graph(self) -> OntologyGraph[ID]:
        """
        :return: the ontology graph with nodes of given type.
        """
        pass


class Versioned(metaclass=abc.ABCMeta):
    """
    Base class for entities that may have version.
    """

    @property
    @abc.abstractmethod
    def version(self) -> typing.Optional[str]:
        """
        :return: version `str` or `None` if the version is not available.
        """
        pass
