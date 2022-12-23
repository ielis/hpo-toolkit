import typing
from collections import deque

from hpotk.model import TermId
from hpotk.graph import OntologyGraph, GraphAware


# TODO - write docs


def get_ancestors(g: typing.Union[GraphAware, OntologyGraph], source: TermId, include_source: bool = False) -> typing.Generator[TermId, None, None]:
    g = _check_ontology_graph_is_available(g)

    # Init
    buffer: typing.Deque[TermId] = deque()
    if include_source:
        buffer.append(source)
    else:
        for parent in g.get_parents(source):
            buffer.append(parent)

    # Loop
    while buffer:
        current = buffer.popleft()
        for parent in g.get_parents(current):
            buffer.append(parent)
        yield current


def get_parents(g: typing.Union[GraphAware, OntologyGraph], source: TermId, include_source: bool = False) -> typing.Generator[TermId, None, None]:
    g = _check_ontology_graph_is_available(g)

    if include_source:
        yield source
    for parent in g.get_parents(source):
        yield parent


def get_descendents(g: typing.Union[GraphAware, OntologyGraph], source: TermId, include_source: bool = False) -> typing.Generator[TermId, None, None]:
    g = _check_ontology_graph_is_available(g)

    buffer: typing.Deque[TermId] = deque()
    if include_source:
        buffer.append(source)
    else:
        for child in g.get_children(source):
            buffer.append(child)

    while buffer:
        current = buffer.popleft()
        for child in g.get_children(current):
            buffer.append(child)
        yield current


def get_children(g: typing.Union[GraphAware, OntologyGraph], source: TermId, include_source: bool = False) -> typing.Generator[TermId, None, None]:
    g = _check_ontology_graph_is_available(g)

    if include_source:
        yield source
    for child in g.get_children(source):
        yield child


def exists_path(g: typing.Union[GraphAware, OntologyGraph], source: TermId, destination: TermId) -> bool:
    g = _check_ontology_graph_is_available(g)

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
