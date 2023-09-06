import abc
import typing

from hpotk.model import ID, CURIE_OR_TERM_ID_OR_IDENTIFIED, TERM, MINIMAL_TERM, Versioned
from hpotk.graph import GraphAware


class MinimalOntology(typing.Generic[ID, MINIMAL_TERM], GraphAware[ID], Versioned, metaclass=abc.ABCMeta):
    """
    `MinimalOntology` is a value object that mostly holds the ontology data.

    The typical way to load the ontology is by parsing Obographs JSON file:

    .. doctest:: minimal-ontology-api

      >>> import hpotk
      >>> hpo = hpotk.ontology.load.obographs.load_minimal_ontology('data/hp.toy.json')

    The ontology data comprises:

    * ontology graph as :class:`hpotk.graph.OntologyGraph`,
    * ontology concepts as :class:`hpotk.model.MinimalTerm`, and
    * the version of the data.

    The ontology acts as a Python container of term IDs, we can check if a term is in the ontology as:

    .. doctest:: minimal-ontology-api

      >>> seizure_curie = 'HP:0001250'
      >>> seizure_curie in hpo
      True

    This works for term IDs too:

    .. doctest:: minimal-ontology-api

      >>> seizure_id = hpotk.TermId.from_curie(seizure_curie)
      >>> seizure_id in hpo
      True

    The ontology has length - the number of *primary* terms:

    .. doctest:: minimal-ontology-api

      >>> len(hpo)
      393

    .. note::

      The toy HPO has only 393 terms. Real-life HPO has much more terms...
    """

    @property
    @abc.abstractmethod
    def term_ids(self) -> typing.Iterator[ID]:
        """
        Get an iterator over term IDs of the primary AND obsolete ontology terms.
        """
        pass

    @property
    @abc.abstractmethod
    def terms(self) -> typing.Iterator[MINIMAL_TERM]:
        """
        Get an iterator over current terms (*not* obsolete terms).
        """
        pass

    @abc.abstractmethod
    def get_term(self, term_id: CURIE_OR_TERM_ID_OR_IDENTIFIED) -> typing.Optional[MINIMAL_TERM]:
        """
        Get the current term for a `term_id`.

        .. doctest:: minimal-ontology-api

          >>> seizure = hpo.get_term('HP:0001250')
          >>> seizure.name
          'Seizure'

        :param term_id: a CURIE `str` (e.g. 'HP:1234567'), a :class:`hpotk.model.TermId` or
         an :class:`hpotk.model.Identified` entity that represents a *current* or an *obsolete* term.
        :return: the current term or `None` if the ontology does not contain the term ID.
        """
        pass

    def get_term_name(self, term_id: CURIE_OR_TERM_ID_OR_IDENTIFIED) -> typing.Optional[str]:
        """
        Get the name of the term with a `term_id`.

        .. doctest:: minimal-ontology-api

          >>> seizure_name = hpo.get_term_name('HP:0001250')
          >>> seizure_name
          'Seizure'

        :param term_id: a CURIE `str` (e.g. 'HP:1234567'), a :class:`hpotk.model.TermId` or
         an :class:`hpotk.model.Identified` entity that represents a *current* or an *obsolete* term.
        :return: name of the term if the term is in ontology or `None` otherwise.
        """
        term = self.get_term(term_id)
        return term.name if term else None


    def __contains__(self, term_id: CURIE_OR_TERM_ID_OR_IDENTIFIED) -> bool:
        """
        Test if the ontology contains a `term_id`.

        Use :func:`get_term` if you want to use the corresponding term apart from knowing that it is there.

        .. doctest:: minimal-ontology-api

          >>> assert 'HP:0001250' in hpo
          >>> assert hpotk.TermId.from_curie('HP:0001250') in hpo
          >>> assert seizure in hpo

        :param term_id: a CURIE `str` (e.g. HP:1234567'), a :class:`hpotk.model.TermId` or
         an :class:`hpotk.model.Identified` entity that represents a *current* or an *obsolete* term.
        :return: `True` if the term is in the ontology and `False` otherwise.
        """
        return self.get_term(term_id) is not None

    @abc.abstractmethod
    def __len__(self):
        """
        Get the number of the primary (non-obsolete) terms in the ontology.
        
        .. doctest:: minimal-ontology-api

          >>> len(hpo)
          393

        :return: the number of primary terms
        """
        pass


class Ontology(MinimalOntology[ID, TERM], metaclass=abc.ABCMeta):
    """
    An ontology with all information available for terms.
    """
    pass
