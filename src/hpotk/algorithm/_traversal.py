import typing
from warnings import warn
from collections import deque

from hpotk.model import TermId, CURIE_OR_TERM_ID
from hpotk.graph import OntologyGraph, GraphAware


def get_ancestors(g: typing.Union[GraphAware, OntologyGraph],
                  source: CURIE_OR_TERM_ID,
                  include_source: bool = False) -> typing.FrozenSet[TermId]:
    """
    Get all ancestor :class:`TermId`\\ (s). of the `source` term (parents, grandparents, great-grandparents etc.)..

    The method raises a :class:`ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: `:class:`TermId` or a term ID curie as a `str (e.g. `HP:1234567`)
    :param include_source: whether to include the `source` term in the resulting set
    :return: a `frozenset` with ancestor :class:`TermId`\\ (s).
    """
    # Check
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)

    # Init
    buffer: typing.Deque[TermId] = deque()
    if include_source:
        buffer.append(source)
    else:
        for parent in g.get_parents(source):
            buffer.append(parent)

    # Loop
    builder: typing.Set[TermId] = set()
    while buffer:
        current = buffer.popleft()
        for parent in g.get_parents(current):
            buffer.append(parent)
        builder.add(current)
    return frozenset(builder)


def get_parents(g: typing.Union[GraphAware, OntologyGraph],
                source: CURIE_OR_TERM_ID,
                include_source: bool = False) -> typing.FrozenSet[TermId]:
    """
    Get :class:`TermId`\\ (s). of the direct parents of the `source` term.

    The method raises a :class:`ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: :class:`TermId` or a term ID curie as a :class:`str (e.g. `HP:1234567`)
    :param include_source:  whether to include the `source` term ID(s) in the results
    :return: a :class:`frozenset` with parent `TermId`s
    """
    # Check
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)

    # Init
    builder: typing.Set[TermId] = set()
    if include_source:
        builder.add(source)

    # Loop
    for parent in g.get_parents(source):
        builder.add(parent)
    return frozenset(builder)


def get_descendants(g: typing.Union[GraphAware, OntologyGraph],
                    source: CURIE_OR_TERM_ID,
                    include_source: bool = False) -> typing.FrozenSet[TermId]:
    """
    Get all descendants `TermId`s of the `source` term (children, grandchildren, great-grandchildren etc.)..

    The method raises a `ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: `TermId` or a term ID curie as a `str (e.g. `HP:1234567`)
    :param include_source:  whether to include the `source` term ID(s) in the results
    :return: a :class:`frozenset` with descendants `TermId`s
    """
    # Check
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)

    # Init
    buffer: typing.Deque[TermId] = deque()
    if include_source:
        buffer.append(source)
    else:
        for child in g.get_children(source):
            buffer.append(child)

    # Loop
    builder: typing.Set[TermId] = set()
    while buffer:
        current = buffer.popleft()
        for child in g.get_children(current):
            buffer.append(child)
        builder.add(current)
    return frozenset(builder)


def get_descendents(g: typing.Union[GraphAware, OntologyGraph],
                    source: CURIE_OR_TERM_ID,
                    include_source: bool = False) -> typing.FrozenSet[TermId]:
    """
    Get all descendants `TermId`s of the `source` term (children, grandchildren, great-grandchildren etc.)..

    The method raises a `ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: `TermId` or a term ID curie as a `str (e.g. `HP:1234567`)
    :param include_source: whether to include the `source` term in the resulting set
    :return: a `frozenset` with descendants `TermId`s
    """
    # TODO[v0.3.0] - remove the deprecated method
    warn('The method is deprecated due to typo and will be removed in v0.3.0. Use get_descendants() instead',
         DeprecationWarning, stacklevel=2)
    return get_descendants(g, source, include_source)


def get_children(g: typing.Union[GraphAware, OntologyGraph],
                 source: CURIE_OR_TERM_ID,
                 include_source: bool = False) -> typing.FrozenSet[TermId]:
    """
    Get `TermId`s of the direct children of the `source` term.

    The method raises a `ValueError` if inputs do not meet the requirement described below.

    :param g: the ontology graph or a graph-aware entity
    :param source: `TermId` or a CURIE `str` (e.g. `HP:1234567`)
    :param include_source: whether to include the `source` term in the resulting set
    :return: a `frozenset` with children `TermId`s
    """
    # Check
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)

    # Init
    builder: typing.Set[TermId] = set()
    if include_source:
        builder.add(source)

    # Loop
    for child in g.get_children(source):
        builder.add(child)
    return frozenset(builder)


def exists_path(g: typing.Union[GraphAware, OntologyGraph],
                source: CURIE_OR_TERM_ID,
                destination: CURIE_OR_TERM_ID) -> bool:
    """
    Return `True` if `destination` is an ancestor of the `source` term.

    The path does *not* exists if `source` and `destination` are the same term.

    :param g: the ontology graph or a graph-aware entity
    :param source: `TermId` or a CURIE `str` (e.g. `HP:1234567`)
    :param destination: `TermId` or a CURIE `str` (e.g. `HP:1234567`)
    :return: `True` if a path exists from `source` to `destination`
    """
    g = _check_ontology_graph_is_available(g)
    source = _check_curie_or_term_id(source)
    destination = _check_curie_or_term_id(destination)

    if source == destination:
        return False

    for ancestor in get_ancestors(g, source):
        if ancestor == destination:
            return True

    return False


def _check_ontology_graph_is_available(g):
    if isinstance(g, OntologyGraph):
        pass
    elif isinstance(g, GraphAware):
        g = g.graph
    else:
        raise ValueError(f'`g` must implement `OntologyGraph` or `GraphAware` but got {type(g)}')
    return g


def _check_curie_or_term_id(source: CURIE_OR_TERM_ID) -> TermId:
    if isinstance(source, str):
        source = TermId.from_curie(source)
    elif isinstance(source, TermId):
        pass
    else:
        raise ValueError(f'`source` must be `TermId` or a CURIE `str` but got {type(source)}')
    return source
