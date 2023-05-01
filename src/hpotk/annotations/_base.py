import abc
import enum
import typing

from hpotk.model import Identified, Named, Versioned, TermId
from hpotk.model import CURIE_OR_TERM_ID
from ._api import ObservableAnnotation, AnnotatedItem, AnnotatedItemContainer


class Ratio(metaclass=abc.ABCMeta):

    @staticmethod
    def create(numerator: int, denominator: int):
        return SimpleRatio(numerator, denominator)

    @property
    @abc.abstractmethod
    def numerator(self) -> int:
        pass

    @property
    @abc.abstractmethod
    def denominator(self) -> int:
        pass

    @property
    def frequency(self) -> float:
        return self.numerator / self.denominator

    def is_positive(self) -> bool:
        return self.numerator > 0

    def is_zero(self) -> bool:
        return self.numerator == 0

    @staticmethod
    def fold(left, right):
        """
        Fold two :class:`Ratio`s together into a new :class:`Ratio` that represents `n` over `m` of both inputs.

        Note that this is *NOT* the addition of two :class:`Ratio`s!

        For instance, if :math:`n_1` of :math:`m_1` and :math:`n_2` of :math:`m_2` population members like lasagna,
        then :math:`n_1 + n_2` of :math:`m_1 + m_2` people like lasagna in total.

        :param left: left :class:`Ratio`.
        :param right: right :class:`Ratio`.
        :return: the result as a :class:`SimpleRatio`.
        """
        if isinstance(left, Ratio) and isinstance(right, Ratio):
            return SimpleRatio(left.numerator + right.numerator, left.denominator + right.denominator)
        else:
            msg = 'left arg must be an instance of `Ratio`' \
                if isinstance(right, Ratio) \
                else 'right arg must be an instance of `Ratio`'
            raise ValueError(msg)

    def __eq__(self, other):
        return isinstance(other, Ratio) \
            and self.numerator * other.denominator == other.numerator * self.denominator

    def __str__(self):
        return f"{self.numerator}/{self.denominator}"


class SimpleRatio(Ratio):

    def __init__(self, numerator: int, denominator: int):
        if not isinstance(numerator, int) or numerator < 0:
            raise ValueError(f'Numerator {numerator} must be a non-negative `int`')
        if not isinstance(denominator, int) or denominator <= 0:
            raise ValueError(f'Denominator {denominator} must be a positive `int`')
        self._numerator = numerator
        self._denominator = denominator

    @property
    def numerator(self) -> int:
        return self._numerator

    @property
    def denominator(self) -> int:
        return self._denominator

    def __eq__(self, other):
        if isinstance(other, SimpleRatio):
            return self._numerator * other._denominator == self._denominator * other._numerator
        else:
            return super().__eq__(other)

    def __repr__(self):
        return f"SimpleRatio(" \
               f"numerator={self._numerator}, " \
               f"denominator={self._denominator})"


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


class HpoDiseaseAnnotation(ObservableAnnotation, metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def ratio(self) -> Ratio:
        """
        :return: ratio representing a total number of the cohort members who displayed presence
                 of the phenotypic feature represented by :class:`HpoDiseaseAnnotation` at some point in their life.
        """
        pass

    @property
    def is_present(self) -> bool:
        return not self.ratio.is_zero()

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
               f"identifier={self.identifier}, " \
               f"ratio={self.ratio}, " \
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
