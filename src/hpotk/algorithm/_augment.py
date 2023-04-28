import typing

from hpotk.graph import GraphAware, OntologyGraph
from hpotk.model import TermId
from ._traversal import get_ancestors, get_descendants


def augment_with_ancestors(g: typing.Union[GraphAware, OntologyGraph],
                           source: typing.Union[TermId, typing.Collection[TermId]],
                           include_source: bool = False) -> frozenset[TermId]:
    """
    Get a set of ancestors of the source :class:`TermId`\\ (s).
    The ancestor set may or may not include the source term IDs depending on the value of `include_source` argument.

    :param g: an ontology graph or an ontology graph-aware item
    :param source: source term ID or a collection of term IDs.
    :param include_source:  whether to include the `source` term ID(s) in the results
    :return: a :class:`frozenset` with ancestor :class:`TermId`\ s
    """
    return _augment_impl(g, source, include_source, get_ancestors)


def augment_with_descendants(g: typing.Union[GraphAware, OntologyGraph],
                             source: typing.Union[TermId, typing.Collection[TermId]],
                             include_source: bool = False) -> frozenset[TermId]:
    """
    Get a set of descendants of the source :class:`TermId`\\ (s).
    The descendant set may or may not include the source term IDs depending on the value of `include_source` argument.

    :param g: an ontology graph or an ontology graph-aware item
    :param source: source term ID or a collection of term IDs.
    :param include_source:  whether to include the `source` term ID(s) in the results
    :return: a :class:`frozenset` with descendant :class:`TermId`\ s
    """
    return _augment_impl(g, source, include_source, get_descendants)


def _augment_impl(g: typing.Union[GraphAware, OntologyGraph],
                  source: typing.Union[TermId, typing.Collection[TermId]],
                  include_source: bool,
                  func: typing.Callable[[typing.Union[GraphAware, OntologyGraph], TermId, bool], frozenset[TermId]]) \
        -> frozenset[TermId]:
    if not (isinstance(g, GraphAware) or isinstance(g, OntologyGraph)):
        raise ValueError(f'hpo must be instance of GraphAware or an OntologyGraph but was {type(g)}')
    if isinstance(source, TermId):
        return get_ancestors(g, source, include_source)
    elif isinstance(source, typing.Collection):
        augmented_term_ids = set()
        for term_id in source:
            for augmented in func(g, term_id, include_source):
                augmented_term_ids.add(augmented)
        return frozenset(augmented_term_ids)
    else:
        raise ValueError(f'source should be a TermId or a Collection of TermIds but got a {type(source)}')
