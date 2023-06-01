import abc
import enum
import typing

from hpotk.model import Identified, Named, TermId
from hpotk.model import CURIE_OR_TERM_ID
from ._api import FrequencyAwareFeature, AnnotatedItem, AnnotatedItemContainer


class EvidenceCode(enum.Enum):
    """Inferred from electronic evidence."""
    IEA = enum.auto()
    """Traceable author statement."""
    TAS = enum.auto()
    """Published clinical study."""
    PCS = enum.auto()

    @staticmethod
    def parse(value: str):
        """
        Parse evidence code from `str` value.

        :param value: a str with the evidence code.
        :return: the parsed enum member or `None` if `value` is not valid `EvidenceCode` value.
        """
        value = value.upper()
        if value == 'IEA':
            return EvidenceCode.IEA
        elif value == 'TAS':
            return EvidenceCode.TAS
        elif value == 'PCS':
            return EvidenceCode.PCS
        else:
            return None


class Sex(enum.Enum):
    UNKNOWN = enum.auto()
    MALE = enum.auto()
    FEMALE = enum.auto()

    @staticmethod
    def parse(value: str):
        """
        Parse :class:`Sex` from :class:`str` value.

        :param value: a `str` with the sex code.
        :return: the parsed enum member or `None` if `value` is not valid :class:`Sex` value.
        """
        value = value.upper()
        if value == 'MALE':
            return Sex.MALE
        elif value == 'FEMALE':
            return Sex.FEMALE
        elif value == 'UNKNOWN':
            return Sex.UNKNOWN
        else:
            return None


class AnnotationReference(Identified):

    def __init__(self, identifier: TermId,
                 evidence_code: EvidenceCode):
        if not isinstance(identifier, TermId):
            raise ValueError(f'Identifier {identifier} is not a `TermId`')
        if not isinstance(evidence_code, EvidenceCode):
            raise ValueError(f'Evidence code {evidence_code} is not an `EvidenceCode`')
        self._identifier = identifier
        self._evidence_code = evidence_code

    @property
    def identifier(self) -> TermId:
        return self._identifier

    @property
    def evidence_code(self) -> EvidenceCode:
        return self._evidence_code

    def __eq__(self, other):
        return isinstance(other, AnnotationReference) \
            and self.identifier == other.identifier \
            and self.evidence_code == other.evidence_code

    def __hash__(self):
        return hash((self._identifier, self._evidence_code))

    def __str__(self):
        return f"AnnotationReference(" \
               f"identifier={self._identifier}, " \
               f"evidence_code={self._evidence_code})"

    def __repr__(self):
        return f"AnnotationReference(" \
               f"identifier={repr(self._identifier)}, " \
               f"evidence_code={repr(self._evidence_code)})"


class HpoDiseaseAnnotation(Identified, FrequencyAwareFeature, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def references(self) -> typing.List[AnnotationReference]:
        """
        :return: a list of `AnnotationReference`s that support presence/absence of the disease annotation
        """
        pass

    @property
    @abc.abstractmethod
    def modifiers(self) -> typing.List[TermId]:
        """
        :return: a list of disease annotation modifiers
        """
        pass

    def __str__(self):
        return f"HpoDiseaseAnnotation(" \
               f"identifier={self.identifier.value}, " \
               f"frequency={self.numerator}/{self.denominator}, " \
               f"references={self.references}, " \
               f"modifiers={self.modifiers})"

    def __repr__(self):
        return f"HpoDiseaseAnnotation(" \
               f"identifier={self.identifier}, " \
               f"numerator={self.numerator}, " \
               f"denominator={self.denominator}, " \
               f"references={self.references}, " \
               f"modifiers={self.modifiers})"


class HpoDisease(AnnotatedItem[HpoDiseaseAnnotation], Identified, Named, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def modes_of_inheritance(self) -> typing.Collection[TermId]:
        """
        :return: a collection of modes of inheritance associated with the disease.
        """
        pass

    def __str__(self):
        return f"HpoDisease(" \
               f"identifier={self.identifier}, " \
               f"name={self.name}, " \
               f"n_annotations={len(self.annotations)})"


class HpoDiseases(AnnotatedItemContainer[HpoDiseaseAnnotation], metaclass=abc.ABCMeta):
    """
    A container for a set of :class:`HpoDisease`s that allows iteration over all diseases,
    knows about the number of diseases in the container, and supports retrieval of the disease by its identifier.
    """

    @abc.abstractmethod
    def __getitem__(self, disease_id: CURIE_OR_TERM_ID) -> typing.Optional[HpoDisease]:
        """
        Get :class:`HpoDisease` based on given `disease_id` or `None` if the disease for the identifier is not present
        in the container.

        :param disease_id: a `str` or :class:`TermId` of the disease
        :return: :class:`HpoDisease` or `None`
        """
        pass

    def __str__(self):
        return f"HpoDiseases(n_diseases={len(self)}, " \
               f"version={self.version})"
