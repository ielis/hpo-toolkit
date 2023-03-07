import typing

from hpotk.model import TermId
from ._disease import AnnotationReference, Ratio
from ._disease import HpoDisease, HpoDiseaseAnnotation


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
