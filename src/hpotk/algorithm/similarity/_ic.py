import math
import typing
from collections import Counter

from hpotk.annotations import AnnotatedItemContainer
from hpotk.graph import OntologyGraph, GraphAware
from hpotk.model import TermId
from .._augment import augment_with_ancestors


def calculate_ic_for_annotated_items(items: AnnotatedItemContainer,
                                     graph: typing.Union[GraphAware, OntologyGraph],
                                     base: typing.Optional[float] = None) -> typing.Mapping[TermId, float]:
    """
    Calculate information content (IC) for each :class:`TermId` based on a collection of annotated `items`.

    :param items: a collection of :class:`hpotk.annotations.AnnotatedItem`\ s
    :param graph: ontology graph or an object that has the ontology graph
    :param base: information content base or `None` for *e*
                 (produces IC in `nats <https://en.wikipedia.org/wiki/Nat_(unit)>`_)
    :return: a mapping from :class:`TermId` to information content in nats, bits, or else, depending on the `base` value
    """
    if isinstance(graph, GraphAware):
        root = graph.graph.root
    elif isinstance(graph, OntologyGraph):
        root = graph.root
    else:
        raise ValueError(f'graph must be either an instance of `OntologyGraph` or `GraphAware` '
                         f'but it was {type(graph)}')

    hit_count = Counter()

    for i, item in enumerate(items):
        for annotation in item.annotations:
            if annotation.is_present:
                for ancestor in augment_with_ancestors(graph, annotation.identifier, include_source=True):
                    hit_count[ancestor] += 1

    log_func = math.log if base is None else lambda c: math.log(c, base)

    population_count = hit_count[root]
    return {
        term_id: -log_func(count / population_count) for term_id, count in hit_count.items()
    }
