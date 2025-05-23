import typing

from hpotk.util import validate_instance, validate_optional_instance
from hpotk.graph import OntologyGraph
from hpotk.model import TermId, Identified
from ._api import Ontology, MinimalOntology
from ._api import ID, MINIMAL_TERM, TERM, CURIE_OR_TERM_ID_OR_IDENTIFIED


class DefaultMinimalOntology(MinimalOntology[ID, MINIMAL_TERM]):

    def __init__(self, graph: OntologyGraph[ID],
                 current_terms: typing.Sequence[MINIMAL_TERM],
                 term_id_to_term: typing.Mapping[ID, MINIMAL_TERM],
                 version: typing.Optional[str] = None):
        self._graph = validate_instance(graph, OntologyGraph, 'graph')
        self._current_terms = current_terms
        self._term_id_to_term = term_id_to_term
        self._version = validate_optional_instance(version, str, 'version')

    @property
    def graph(self) -> OntologyGraph[ID]:
        return self._graph

    @property
    def term_ids(self) -> typing.Iterator[ID]:
        return iter(self._term_id_to_term.keys())

    @property
    def terms(self) -> typing.Iterator[MINIMAL_TERM]:
        return iter(self._current_terms)

    def get_term(self, term_id: CURIE_OR_TERM_ID_OR_IDENTIFIED) -> typing.Optional[MINIMAL_TERM]:
        term_id = _validate_term_id(term_id)
        try:
            return self._term_id_to_term[term_id]
        except KeyError:
            return None

    @property
    def version(self) -> typing.Optional[str]:
        return self._version

    def __len__(self):
        return len(self._current_terms)


class DefaultOntology(Ontology[ID, TERM]):

    def __init__(self, graph: OntologyGraph[ID],
                 current_terms: typing.Sequence[TERM],
                 term_id_to_term: typing.Mapping[ID, TERM],
                 version: typing.Optional[str] = None):
        self._graph = validate_instance(graph, OntologyGraph, 'graph')
        self._current_terms = current_terms
        self._term_id_to_term = term_id_to_term
        self._version = validate_optional_instance(version, str, 'version')

    @property
    def graph(self) -> OntologyGraph[ID]:
        return self._graph

    @property
    def term_ids(self) -> typing.Iterator[ID]:
        return iter(self._term_id_to_term.keys())

    @property
    def terms(self) -> typing.Iterator[TERM]:
        return iter(self._current_terms)

    def get_term(self, term_id: CURIE_OR_TERM_ID_OR_IDENTIFIED) -> typing.Optional[TERM]:
        term_id = _validate_term_id(term_id)
        try:
            return self._term_id_to_term[term_id]
        except KeyError:
            return None

    @property
    def version(self) -> typing.Optional[str]:
        return self._version

    def __len__(self) -> int:
        return len(self._current_terms)


def create_minimal_ontology(graph: OntologyGraph[ID],
                            terms: typing.Sequence[MINIMAL_TERM],
                            version: typing.Optional[str] = None) -> MinimalOntology[ID, MINIMAL_TERM]:
    """
    Create minimal ontology from the components.

    :param graph: the ontology graph.
    :param terms: ALL ontology terms (both obsolete and primary).
    :param version: ontology version or `None` if unknown.
    :return: the ontology
    """
    current_terms = [term for term in terms if term.is_current]
    term_id_to_term = make_term_id_map(current_terms)
    return DefaultMinimalOntology(graph, current_terms, term_id_to_term, version)


def create_ontology(graph: OntologyGraph[ID],
                    terms: typing.Sequence[TERM],
                    version: typing.Optional[str] = None) -> Ontology[ID, TERM]:
    """
    Create ontology from the components.

    :param graph: the ontology graph.
    :param terms: ALL ontology terms (both obsolete and primary).
    :param version: ontology version or `None` if unknown.
    :return: the ontology.
    """
    current_terms = [term for term in terms if term.is_current]
    term_id_to_term = make_term_id_map(current_terms)
    return DefaultOntology(graph, current_terms, term_id_to_term, version)


def make_term_id_map(terms: typing.Sequence[MINIMAL_TERM]) -> typing.Mapping[ID, MINIMAL_TERM]:
    """
    Create a mapping from primary and alternate IDs to `MINIMAL_TERM`.

    :param terms: current ontology terms
    :return: mapping from primary and alternate IDs to `MINIMAL_TERM`
    """
    data = {}
    for term in terms:
        data[term.identifier] = term
        for alt_id in term.alt_term_ids:
            data[alt_id] = term
    return data


def _validate_term_id(term_id: CURIE_OR_TERM_ID_OR_IDENTIFIED) -> TermId:
    """
    Validate that `term_id` is a `TermId` or a valid CURIE `str`.
    """
    if isinstance(term_id, TermId):
        return term_id
    elif isinstance(term_id, Identified):
        return term_id.identifier
    elif isinstance(term_id, str):
        return TermId.from_curie(term_id)
    else:
        raise ValueError(f'Expected a `str`, a `TermId` or an `Identified` entity but got {type(term_id)}')
