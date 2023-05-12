import math
import typing
from collections import Counter

from hpotk.annotations import AnnotatedItemContainer
from hpotk.ontology import MinimalOntology
from hpotk.util import validate_instance
from ._model import SimpleAnnotationIcContainer, AnnotationIcContainer
from .._augment import augment_with_ancestors


def calculate_ic_for_annotated_items(items: AnnotatedItemContainer,
                                     ontology: MinimalOntology,
                                     base: typing.Optional[float] = None) -> AnnotationIcContainer:
    """
    Calculate information content (IC) for each :class:`TermId` based on a collection of annotated `items`.

    :param items: a collection of :class:`hpotk.annotations.AnnotatedItem`\ s
    :param ontology: ontology with concepts used to annotate the `items`
    :param base: information content base or `None` for *e*
                 (produces IC in `nats <https://en.wikipedia.org/wiki/Nat_(unit)>`_)
    :return: a container with mappings from :class:`TermId` to information content in nats, bits, or else,
             depending on the `base` value
    """
    ontology = validate_instance(ontology, MinimalOntology, 'ontology')

    graph = ontology.graph
    root = graph.root

    hit_count = Counter()

    for item in items:
        for annotation in item.annotations:
            if annotation.is_present:
                for ancestor in augment_with_ancestors(graph, annotation.identifier, include_source=True):
                    hit_count[ancestor] += 1

    log_func = math.log if base is None else lambda c: math.log(c, base)

    population_count = hit_count[root]

    data = {term_id: -log_func(count / population_count) for term_id, count in hit_count.items()}
    metadata = {'annotated_items_version': items.version, 'ontology_version': ontology.version}
    return SimpleAnnotationIcContainer(data, metadata=metadata)
