import math
import typing
from collections import Counter

from hpotk.model import TermId
from hpotk.annotations import AnnotatedItemContainer
from hpotk.ontology import MinimalOntology
from ._model import AnnotationIcContainer


def calculate_ic_for_annotated_items(
    items: AnnotatedItemContainer,
    ontology: MinimalOntology,
    base: typing.Optional[float] = None,
    module_root: typing.Optional[TermId] = None,
    use_pseudocount: bool = False,
) -> AnnotationIcContainer:
    """
    Calculate information content (IC) for each :class:`TermId` based on a collection of annotated `items`.

    The calculation can be done for an ontology module - only the descendants of the provided `module_root`
    will be included in the analysis. If `use_pseudocount` is `True`, then the count of all ontology/module terms
    is set to at least 1, even for those terms that do not annotate the `items`.

    :param items: a collection of world items (e.g. diseases).
    :param ontology: ontology with concepts used to annotate the `items` (e.g. Human Phenotype Ontology for diseases).
    :param base: information content base or `None` for *e*
                 (produces IC in `nats <https://en.wikipedia.org/wiki/Nat_(unit)>`_)
    :param module_root: the root of the ontology module to calculate the IC for.
    :param use_pseudocount: assume that each ontology term annotates at least one item.

    :return: a container with mappings from :class:`TermId` to information content in nats, bits, or else,
             depending on the `base` value
    """
    assert isinstance(ontology, MinimalOntology)

    term_id_count: Counter[TermId] = Counter()
    module_term_ids: typing.Optional[typing.Set[TermId]] = (
        None if module_root is None else set(ontology.graph.get_descendants(module_root, include_source=True))
    )

    for item in items:
        for ann in item.annotations:
            if ann.is_present:
                if module_root is not None and ann.identifier not in module_term_ids:
                    # annotation is not from the target module.
                    continue

                if module_term_ids is None:
                    # Not doing module
                    term_id_count[ann.identifier] += 1
                elif ann.identifier in module_term_ids:
                    # Doing module and the ancestor is from the module
                    term_id_count[ann.identifier] += 1

                for anc in ontology.graph.get_ancestors(ann.identifier):
                    if module_term_ids is None:
                        # Not doing module
                        term_id_count[anc] += 1
                    elif anc in module_term_ids:
                        # Doing module and the ancestor is from the module
                        term_id_count[anc] += 1

    if use_pseudocount:
        # Set the count of all primary term IDs to at least one but DO NOT increment the count of the ancestor
        # that already count>=1 .
        # Note, in the HPO case, this will set count of non-phenotypic abnormalities (e.g. Clinical modifier)
        # to 1 as well.
        corpus = map(lambda t: t.identifier, ontology.terms) if module_root is None else module_term_ids

        for term_id in corpus:  # type: ignore - `term_id_count` is never None if `module_root` is not None
            if term_id not in term_id_count:
                term_id_count[term_id] = 1

    log_func = math.log if base is None else lambda c: math.log(c, base)

    pop_cnt = term_id_count[ontology.graph.root] if module_root is None else term_id_count[module_root]
    data = {term_id: log_func(pop_cnt / cnt) for term_id, cnt in term_id_count.items()}

    metadata = dict()
    if items.version is not None:
        metadata["annotated_items_version"] = items.version
    if ontology.version is not None:
        metadata["ontology_version"] = ontology.version

    return AnnotationIcContainer.from_mapping(data, metadata=metadata)
