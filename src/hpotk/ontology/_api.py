import abc
import typing

from hpotk.model import MinimalTerm, Term
from hpotk.graph import GraphAware

from ._attrs import Versioned
from ._attrs import ID


MINIMAL_TERM = typing.TypeVar('MINIMAL_TERM', bound=MinimalTerm)
TERM = typing.TypeVar('TERM', bound=Term)


class MinimalOntology(typing.Generic[ID, MINIMAL_TERM], GraphAware[ID], Versioned, metaclass=abc.ABCMeta):
    """
    Minimal ontology has the ontology graph and `hpotk.base.model.MinimalTerm`s.
    """

    @property
    @abc.abstractmethod
    def term_ids(self) -> typing.Iterator[ID]:
        """
        :return: an iterator over `TermId`s of primary and obsolete ontology terms
        """
        pass

    @property
    @abc.abstractmethod
    def terms(self) -> typing.Iterator[MINIMAL_TERM]:
        """
        :return: an iterator over current `Term`s (*not* obsolete `Term`s)
        """
        pass

    @abc.abstractmethod
    def get_term(self, term_id: typing.Union[str, ID]) -> typing.Optional[MINIMAL_TERM]:
        """
        Get the current `Term` for a term ID.

        :param term_id: a `TermId` or a CURIE `str` (e.g. 'HP:1234567') representing *current* or *obsolete* term
        :return: the current `Term` or `None` if the ontology does not contain the `TermId`
        """
        pass

    def __contains__(self, term_id: typing.Union[str, ID]) -> bool:
        """
        Test if the ontology contains given `TermId`.

        If you are interested in processing the corresponding term, call `get_term(item)` instead.

        :param term_id: a `TermId` or a CURIE `str` (e.g. 'HP:1234567') representing *current* or *obsolete* term
        :return: `True` if the `TermId` is in the ontology and `False` otherwise
        """
        return self.get_term(term_id) is not None

    @abc.abstractmethod
    def __len__(self):
        """
        Get the number of the primary (non-obsolete) `Term`s in the ontology.

        :return: the number of primary `Term`s
        """
        pass


class Ontology(MinimalOntology[ID, TERM], metaclass=abc.ABCMeta):
    """
    An ontology with all information available for terms.
    """
    pass
