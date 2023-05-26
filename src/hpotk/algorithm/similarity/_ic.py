import math
import typing
from collections import Counter

from hpotk.model import TermId
from hpotk.annotations import AnnotatedItemContainer
from hpotk.ontology import MinimalOntology
from hpotk.util import validate_instance
from ._model import SimpleAnnotationIcContainer, AnnotationIcContainer


def calculate_ic_for_annotated_items(items: AnnotatedItemContainer,
                                     ontology: MinimalOntology,
                                     base: typing.Optional[float] = None,
                                     module_root: typing.Optional[TermId] = None,
                                     assume_annotated: bool = False) -> AnnotationIcContainer:
    """
    Calculate information content (IC) for each :class:`TermId` based on a collection of annotated `items`.

    The calculation can be done for an ontology module - only the descendants of the provided `module_root`
    will be included in the analysis. If `assume_annotated` is `True`, then the count of all ontology/module terms
    is set to at least 1, even for those terms that do not annotate the `items`.

    :param items: a collection of :class:`hpotk.annotations.AnnotatedItem`\ s
    :param ontology: ontology with concepts used to annotate the `items`
    :param base: information content base or `None` for *e*
                 (produces IC in `nats <https://en.wikipedia.org/wiki/Nat_(unit)>`_)
    :param module_root: the root of the ontology module to calculate the IC for.
    :param assume_annotated: assume that each ontology term annotates at least one of the `items`.

    :return: a container with mappings from :class:`TermId` to information content in nats, bits, or else,
             depending on the `base` value
    """
    ontology = validate_instance(ontology, MinimalOntology, 'ontology')

    graph = ontology.graph
    term_id_count: Counter[TermId] = Counter()
    module_term_ids: typing.Optional[typing.Set[TermId]] = None \
        if module_root is None \
        else set(graph.get_descendants(module_root, include_source=True))

    for item in items:
        for annotation in item.annotations:
            if annotation.is_present:
                if module_root is not None and annotation.identifier not in module_term_ids:
                    # annotation is not from the target module.
                    continue

                for ancestor in graph.get_ancestors(annotation.identifier, include_source=True):
                    if module_term_ids is None:
                        # Not doing module
                        term_id_count[ancestor] += 1
                    elif ancestor in module_term_ids:
                        # Doing module and the ancestor is from the module
                        term_id_count[ancestor] += 1

    if assume_annotated:
        # Set the count of all primary term IDs to at least one but DO NOT increment the count of the ancestor
        # that already count>=1 .
        # Note, in the HPO case, this will set count of non-phenotypic abnormalities (e.g. Clinical modifier)
        # to 1 as well.
        corpus = map(lambda t: t.identifier, ontology.terms) \
            if module_root is None \
            else module_term_ids
        for term_id in corpus:
            if term_id not in term_id_count:
                term_id_count[term_id] = 1

    log_func = math.log if base is None else lambda c: math.log(c, base)

    population_count = term_id_count[graph.root] if module_root is None else term_id_count[module_root]

    data = {term_id: -log_func(count / population_count) for term_id, count in term_id_count.items()}
    metadata = {'annotated_items_version': items.version, 'ontology_version': ontology.version}
    return SimpleAnnotationIcContainer(data, metadata=metadata)
