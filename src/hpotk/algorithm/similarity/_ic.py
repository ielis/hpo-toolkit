import math
import typing
from collections import Counter
from typing import Iterator

from hpotk.annotations import AnnotatedItemContainer
from hpotk.graph import OntologyGraph, GraphAware
from hpotk.model import TermId, MetadataAware
from .._augment import augment_with_ancestors


class AnnotationIcContainer(typing.Mapping[TermId, float], MetadataAware):
    """
    A container for information content of item annotations.
    """

    def __init__(self, data: typing.Mapping[TermId, float],
                 metadata: typing.Optional[typing.Mapping[str, str]] = None):
        if not isinstance(data, typing.Mapping):
            raise ValueError(f'data must be an instance of Mapping but it was: {type(data)}')
        self._data = data

        self._meta = dict()
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValueError(f'meta must be a dict but was {type(metadata)}')
            else:
                self._meta.update(metadata)

    def __getitem__(self, key: TermId) -> float:
        return self._data[key]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[TermId]:
        return iter(self._data)

    @property
    def metadata(self) -> typing.Mapping[str, str]:
        return self._meta


def calculate_ic_for_annotated_items(items: AnnotatedItemContainer,
                                     graph: typing.Union[GraphAware, OntologyGraph],
                                     base: typing.Optional[float] = None) -> AnnotationIcContainer:
    """
    Calculate information content (IC) for each :class:`TermId` based on a collection of annotated `items`.

    :param items: a collection of :class:`hpotk.annotations.AnnotatedItem`\ s
    :param graph: ontology graph or an object that has the ontology graph
    :param base: information content base or `None` for *e*
                 (produces IC in `nats <https://en.wikipedia.org/wiki/Nat_(unit)>`_)
    :return: a container with mappings from :class:`TermId` to information content in nats, bits, or else,
             depending on the `base` value
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

    data = {term_id: -log_func(count / population_count) for term_id, count in hit_count.items()}
    metadata = {'version': items.version}
    return AnnotationIcContainer(data, metadata=metadata)
