import abc
import typing

from hpotk.model import MinimalTerm, Term
from hpotk.graph import GraphAware

from ._attrs import Versioned
from ._attrs import ID


MINIMAL_TERM = typing.TypeVar('MINIMAL_TERM', bound=MinimalTerm)
TERM = typing.TypeVar('TERM', bound=Term)


class MinimalOntology(typing.Generic[MINIMAL_TERM, ID], GraphAware[ID], Versioned, metaclass=abc.ABCMeta):
    """
    Minimal ontology has the ontology graph and `hpotk.base.model.MinimalTerm`s.
    """

    @property
    @abc.abstractmethod
    def term_ids(self) -> typing.Iterator:
        """
        :return: an iterator over `TermId`s of primary and obsoleted ontology terms
        """
        pass

    @property
    @abc.abstractmethod
    def terms(self) -> typing.Iterator[MINIMAL_TERM]:
        """
        :return: an iterator over current `Term`s (*not* obsoleted `Term`s)
        """
        pass

    @abc.abstractmethod
    def get_term(self, term_id: ID) -> typing.Optional[MINIMAL_TERM]:
        """
        Get the current `Term` for given `TermId`.

        :param term_id: a `TermId` representing *current* or *obsoleted* `Term`
        :return: the current `Term` or `None` if the ontology does not contain the `TermId`
        """
        pass

    def __contains__(self, item: ID) -> bool:
        """
        Test if the ontology contains given `TermId`.

        If you are interested in processing the corresponding term, call `get_term(item)` instead.

        :param item: a `TermId` representing current or obsoleted `Term`
        :return: `True` if the `TermId` is in the ontology and `False` otherwise
        """
        return self.get_term(item) is not None

    @abc.abstractmethod
    def __len__(self):
        """
        Get the number of the primary (non-obsoleted) `Term`s in the ontology.

        :return: the number of primary `Term`s
        """
        pass


class Ontology(MinimalOntology[TERM], metaclass=abc.ABCMeta):
    """
    An ontology with all information available for terms.
    """
    pass
