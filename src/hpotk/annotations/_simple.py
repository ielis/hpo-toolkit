import typing
import warnings

from hpotk.model import TermId, CURIE_OR_TERM_ID
from ._api import ANNOTATED_ITEM
from ._base import AnnotationReference, Ratio
from ._base import HpoDisease, HpoDiseaseAnnotation, HpoDiseases


class SimpleHpoDiseaseAnnotation(HpoDiseaseAnnotation):

    def __init__(self, identifier: TermId,
                 ratio: Ratio,
                 references: typing.List[AnnotationReference],
                 modifiers: typing.List[TermId]):
        self._id = identifier
        self._ratio = ratio
        self._refs = references
        self._modifiers = modifiers

    @property
    def identifier(self) -> TermId:
        return self._id

    @property
    def ratio(self) -> Ratio:
        return self._ratio

    @property
    def references(self) -> typing.List[AnnotationReference]:
        return self._refs

    @property
    def modifiers(self) -> typing.List[TermId]:
        return self._modifiers


class SimpleHpoDisease(HpoDisease):

    def __init__(self, identifier: TermId,
                 name: str,
                 annotations: typing.Collection[HpoDiseaseAnnotation],
                 modes_of_inheritance: typing.Collection[TermId]):
        self._id = identifier
        self._name = name
        self._annotations = annotations
        self._modes_of_inheritance = modes_of_inheritance

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


class SimpleHpoDiseases(HpoDiseases):

    def __iter__(self) -> typing.Iterator[HpoDiseaseAnnotation]:
        return iter(self._diseases.values())

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

    def __len__(self) -> int:
        return len(self._diseases)

    @property
    def version(self) -> typing.Optional[str]:
        return self._version
