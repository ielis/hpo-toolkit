import typing
import warnings

from hpotk.model import TermId, CURIE_OR_TERM_ID
from ._api import ANNOTATED_ITEM
from ._base import AnnotationReference
from ._base import HpoDisease, HpoDiseaseAnnotation, HpoDiseases, HpoClinicalCourseAnnotation
from ..constants.hpo.clinical_course import get_clinical_course_type


class SimpleHpoDiseaseAnnotation(HpoDiseaseAnnotation):

    def __init__(self, identifier: TermId,
                 numerator: int,
                 denominator: int,
                 references: typing.Sequence[AnnotationReference],
                 modifiers: typing.Sequence[TermId]):
        self._id = identifier
        self.check_numerator_and_denominator(numerator, denominator)
        self._numerator = numerator
        self._denominator = denominator
        self._refs = references
        self._modifiers = modifiers

    @property
    def identifier(self) -> TermId:
        return self._id

    @property
    def numerator(self) -> int:
        return self._numerator

    @property
    def denominator(self) -> int:
        return self._denominator

    @property
    def references(self) -> typing.Sequence[AnnotationReference]:
        return self._refs

    @property
    def modifiers(self) -> typing.Sequence[TermId]:
        return self._modifiers

    def __repr__(self):
        return f"SimpleHpoDiseaseAnnotation(" \
               f"identifier={self.identifier}, " \
               f"numerator={self.numerator}, " \
               f"denominator={self.denominator}, " \
               f"references={self.references}, " \
               f"modifiers={self.modifiers})"


class SimpleHpoClinicalCourseAnnotation(SimpleHpoDiseaseAnnotation):

    def __init__(self, identifier: TermId, numerator: int, denominator: int,
                 references: typing.Sequence[AnnotationReference], modifiers: typing.Sequence[TermId]):
        super().__init__(identifier, numerator, denominator, references, modifiers)
        self._id = identifier

    @property
    def type(self):
        return get_clinical_course_type(self._id)

    def __repr__(self):
        return f"SimpleHpoClinicalCourseAnnotation(" \
               f"identifier={self.identifier}, " \
               f"numerator={self.numerator}, " \
               f"denominator={self.denominator}, " \
               f"references={self.references}, " \
               f"modifiers={self.modifiers})"

class SimpleHpoDisease(HpoDisease):

    def __init__(self, identifier: TermId,
                 name: str,
                 annotations: typing.Collection[HpoDiseaseAnnotation],
                 modes_of_inheritance: typing.Collection[TermId],
                 onset: typing.Collection[TermId],):
        self._id = identifier
        self._name = name
        self._annotations = annotations
        self._modes_of_inheritance = modes_of_inheritance
        self._onset = onset

    @property
    def identifier(self) -> TermId:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def annotations(self) -> typing.Collection[HpoDiseaseAnnotation]:
        return self._annotations

    @property
    def modes_of_inheritance(self) -> typing.Collection[TermId]:
        return self._modes_of_inheritance

    @property
    def onset(self) -> typing.Collection[HpoClinicalCourseAnnotation]:
        return self._onset

class SimpleHpoDiseases(HpoDiseases):

    def __init__(self, diseases: typing.Iterable[HpoDisease], version: str = None):
        self._diseases = {d.identifier: d for d in diseases}
        self._version = version

    @property
    def items(self) -> typing.Collection[ANNOTATED_ITEM]:
        return self._diseases.values()

    @property
    def diseases(self) -> typing.Collection[HpoDisease]:
        # REMOVE(v1.0.0)
        warnings.warn('The `diseases` property has been deprecated and will be removed in `v1.0.0`. '
                      'Use `items()` instead',
                      category=DeprecationWarning, stacklevel=2)
        return self._diseases.values()

    @property
    def disease_ids(self):
        # REMOVE(v1.0.0)
        warnings.warn(f'`disease_ids` property has been deprecated and will be removed in v1.0.0. '
                      f'Iterate over `item_ids()` instead.',
                      DeprecationWarning, stacklevel=2)
        return list(self.item_ids())

    def __getitem__(self, item: CURIE_OR_TERM_ID) -> typing.Optional[HpoDisease]:
        if isinstance(item, TermId):
            pass
        elif isinstance(item, str):
            item = TermId.from_curie(item)
        else:
            raise ValueError(f'Expected a `str` or `TermId` but got {type(item)}')
        try:
            return self._diseases[item]
        except KeyError:
            return None

    def __iter__(self) -> typing.Iterator[HpoDiseaseAnnotation]:
        return iter(self.items)

    def __len__(self) -> int:
        return len(self._diseases)

    @property
    def version(self) -> typing.Optional[str]:
        return self._version
