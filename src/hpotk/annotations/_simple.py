import typing

from hpotk.model import TermId, CURIE_OR_TERM_ID
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
                 annotations: typing.Collection[HpoDiseaseAnnotation]):
        self._id = identifier
        self._name = name
        self._annotations = annotations

    @property
    def identifier(self) -> TermId:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def annotations(self) -> typing.Collection[HpoDiseaseAnnotation]:
        return self._annotations


class SimpleHpoDiseases(HpoDiseases):

    def __init__(self, diseases: typing.Iterable[HpoDisease], version: str = None):
        self._diseases = {d.identifier: d for d in diseases}
        self._version = version

    @property
    def diseases(self) -> typing.Collection[HpoDisease]:
        return self._diseases.values()

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

    @property
    def version(self) -> typing.Optional[str]:
        return self._version
