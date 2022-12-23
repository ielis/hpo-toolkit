import typing

from hpotk.graph import OntologyGraph
from ._api import Ontology, MinimalOntology, ID, TERM, MINIMAL_TERM


class DefaultMinimalOntology(MinimalOntology[ID, MINIMAL_TERM]):

    def __init__(self, graph: OntologyGraph[ID],
                 current_terms: typing.Sequence[MINIMAL_TERM],
                 term_id_to_term: typing.Mapping[ID, MINIMAL_TERM],
                 version: typing.Optional[str] = None):
        self._graph = graph
        self._current_terms = current_terms
        self._term_id_to_term = term_id_to_term
        self._version = version

    @property
    def graph(self) -> OntologyGraph[ID]:
        return self._graph

    @property
    def term_ids(self) -> typing.Iterator:
        return iter(self._term_id_to_term.keys())

    @property
    def terms(self) -> typing.Iterator[MINIMAL_TERM]:
        return iter(self._current_terms)

    def get_term(self, term_id: ID) -> typing.Optional[MINIMAL_TERM]:
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
        self._graph = graph
        self._current_terms = current_terms
        self._term_id_to_term = term_id_to_term
        self._version = version

    @property
    def graph(self) -> OntologyGraph[ID]:
        return self._graph

    @property
    def term_ids(self) -> typing.Iterator:
        return iter(self._term_id_to_term.keys())

    @property
    def terms(self) -> typing.Iterator[TERM]:
        return self._current_terms

    def get_term(self, term_id: ID) -> typing.Optional[TERM]:
        try:
            return self._term_id_to_term[term_id]
        except KeyError:
            return None

    @property
    def version(self) -> typing.Optional[str]:
        return self._version

    def __len__(self):
        return len(self._current_terms)


def create_minimal_ontology(graph: OntologyGraph[ID],
                            terms: typing.Sequence[MINIMAL_TERM],
                            version: typing.Optional[str] = None) -> MinimalOntology[ID, MINIMAL_TERM]:
    """
    Create minimal ontology from the arguments.

    :param graph: the ontology graph
    :param terms: ALL ontology terms (both obsolete and primary)
    :param version: ontology version or `None` if unknown
    :return: the ontology
    """
    current_terms = [term for term in terms if term.is_current]
    term_id_to_term = make_term_id_map(current_terms)
    return DefaultMinimalOntology(graph, current_terms, term_id_to_term, version)


def create_ontology(graph: OntologyGraph[ID],
                    terms: typing.Sequence[TERM],
                    version: typing.Optional[str] = None) -> Ontology[ID, TERM]:
    """
    Create ontology from the arguments.

    :param graph: the ontology graph
    :param terms: ALL ontology terms (both obsolete and primary)
    :param version: ontology version or `None` if unknown
    :return: the ontology
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
