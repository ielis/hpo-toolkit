import functools
import logging
import re
import typing

from hpotk.constants.hpo.base import PHENOTYPIC_ABNORMALITY
from hpotk.model import TermId
from hpotk.ontology import MinimalOntology
from ._ic import AnnotationIcContainer
from ._model import SimilarityContainer
from .._traversal import get_descendants, get_ancestors, get_children

# implement Resnik IC computation starting from a collection of world documents
# and see if we can plug in excluded into the values.

HPO_PATTERN = re.compile(r"HP:(?P<ID>\d{7})")

logger = logging.getLogger('hpotk.algorithm.similarity')


def _get_common_ancestors(hpo: MinimalOntology,
                          left: TermId,
                          right: TermId) -> typing.FrozenSet[TermId]:
    la = get_ancestors(hpo, left, include_source=True)
    ra = get_ancestors(hpo, right, include_source=True)
    return la.intersection(ra)


def precalculate_ic_mica_for_hpo_concept_pairs(ic: AnnotationIcContainer,
                                               hpo: MinimalOntology) -> SimilarityContainer:
    """
    Precalculate Resnik semantic similarity for HPO :class:`TermId` pairs.

    :param ic: a mapping for obtaining an information content of a :class:`TermId`.
    :param hpo: HPO ontology.
    :return: a mapping with Resnik similarity for :class:`TermId` pairs where the similarity :math:`s>0`.
    """
    metadata = {'hpo_version': hpo.version}
    metadata.update(ic.metadata)
    data = SimilarityContainer(metadata=metadata)
    groups = list(get_children(hpo, PHENOTYPIC_ABNORMALITY))
    count = 0
    for section_top in groups:
        term = hpo.get_term(section_top)
        term_ids = list(get_descendants(hpo, section_top, include_source=True))
        logger.info(f'Calculating for {term.name} with {len(term_ids) - 1} descendants')
        for i in range(len(term_ids)):
            left = term_ids[i]
            for j in range(i, len(term_ids)):
                right = term_ids[j]

                ic_mica = functools.reduce(max,
                                           map(lambda term_id: ic.get(term_id, 0.),
                                               _get_common_ancestors(hpo, left, right)),
                                           0.)

                if left.value < right.value:
                    a, b = left.value, right.value
                else:
                    a, b = right.value, left.value

                if ic_mica > 0.:
                    previous = data.get_similarity(a, b)
                    data.set_similarity(a, b, max(ic_mica, previous))
                    count += 1
                if count % 5_000 == 0 and count != 0:
                    logger.info(f'Processed {count:,d} term pairs')

    return data
