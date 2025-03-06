"""
The `hpotk.annotations` module provides classes for working with HPO annotation data that is available for download
from `HPO release data <https://hpo.jax.org/app/data/annotations>`_.

The module contains data classes to model the annotation data. Most notable classes include :class:`HpoDiseases`,
a container of diseases, and :class:`HpoDisease` a representation of the disease data.

The :mod:`hpotk.annotations.load` module contains code for loading the annotations into from HPO annotations format.
"""

from ._api import AnnotatedItem, AnnotatedItemContainer, ANNOTATED_ITEM, ANNOTATION
from ._base import EvidenceCode, Sex, AnnotationReference, HpoClinicalCourseAnnotation
from ._base import HpoDiseaseAnnotation, HpoDisease, HpoDiseases

from ._simple import SimpleHpoDiseaseAnnotation, SimpleHpoDisease, SimpleHpoDiseases, SimpleHpoClinicalCourseAnnotation

from . import load

__all__ = [
    'HpoDiseases', 'HpoDisease', 'HpoDiseaseAnnotation', 'HpoClinicalCourseAnnotation',
    'AnnotatedItem', 'AnnotatedItemContainer', 'ANNOTATED_ITEM', 'ANNOTATION',
    'EvidenceCode', 'Sex', 'AnnotationReference',
    'SimpleHpoDiseaseAnnotation', 'SimpleHpoDisease', 'SimpleHpoDiseases', 'SimpleHpoClinicalCourseAnnotation'
]
