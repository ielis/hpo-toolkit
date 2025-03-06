import abc
import enum
import typing

from hpotk.model import Identified, Named, TermId
from hpotk.model import CURIE_OR_TERM_ID
from ._api import FrequencyAwareFeature, AnnotatedItem, AnnotatedItemContainer


class EvidenceCode(enum.Enum):
    """
    An enumeration with evidence codes.
    """

    IEA = enum.auto()
    """
    Inferred from electronic evidence.
    """

    TAS = enum.auto()
    """
    Traceable author statement.
    """

    PCS = enum.auto()
    """
    Published clinical study.
    """

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
    """
    An enum representing values of apparent biological sex.

    .. note::

      We do not attempt to model all contemporary complexities of the sex.
    """

    UNKNOWN = enum.auto()
    MALE = enum.auto()
    FEMALE = enum.auto()

    @staticmethod
    def parse(value: str):
        """
        Parse :class:`Sex` from a `str` value.

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
    """
    `HpoDiseaseAnnotation` models data of a single disease annotation.

    The annotation has the following attributes:

    * `identifier` - annotation ID, e.g. `HP:0001250`
    * frequency-related attributes of the annotation, such as `frequency` (see :class:`FrequencyAwareFeature` for more info)
    * `references` - a sequence of cross-references that support presence/absence of the annotation
    * `modifiers` - a sequence of clinical modifiers of the annotation, such as age of onset, severity, laterality, ...
    """

    @property
    @abc.abstractmethod
    def references(self) -> typing.Sequence[AnnotationReference]:
        """
        :return: a list of annotation references that support presence/absence of the disease annotation
        """
        pass

    @property
    @abc.abstractmethod
    def modifiers(self) -> typing.Sequence[TermId]:
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

class HpoClinicalCourseAnnotation(HpoDiseaseAnnotation):

    def __str__(self):
        return f"HpoClinicalCourseAnnotation(" \
               f"identifier={self.identifier.value}, " \
               f"frequency={self.numerator}/{self.denominator}, " \
               f"references={self.references}, " \
               f"modifiers={self.modifiers})"

    def __repr__(self):
        return f"HpoClinicalCourseAnnotation(" \
               f"identifier={self.identifier}, " \
               f"numerator={self.numerator}, " \
               f"denominator={self.denominator}, " \
               f"references={self.references}, " \
               f"modifiers={self.modifiers})"

class HpoDisease(AnnotatedItem[HpoDiseaseAnnotation], Identified, Named, metaclass=abc.ABCMeta):
    """
    `HpoDisease` represents a computational model of a rare disease.

    The model includes attributes:

    * `identifier` - disease ID, e.g. `OMIM:256000`
    * `name` - human-readable disease name, e.g. `LEIGH SYNDROME; LS`
    * `annotations` - the phenotype annotations of the disease. See :class:`AnnotatedItem` for more details on
      *all* annotation-related methods
    * `modes_of_inheritance` - a collection of the modes of inheritance associated with the disease

    """

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
    A container for HPO diseases that allows iteration over all diseases,
    knows about the number of diseases in the container, and supports retrieval of the disease by its identifier.
    """

    @abc.abstractmethod
    def __getitem__(self, disease_id: CURIE_OR_TERM_ID) -> typing.Optional[HpoDisease]:
        """
        Get :class:`HpoDisease` based on given `disease_id` or `None` if the disease for the identifier is not present
        in the container.

        :param disease_id: a CURIE `str` or a :class:`TermId` of the disease identifier.
        :return: :class:`HpoDisease` or `None`
        """
        pass

    def __str__(self):
        return f"HpoDiseases(n_diseases={len(self)}, " \
               f"version={self.version})"
