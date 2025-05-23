import re
import enum
import typing
from collections import defaultdict, namedtuple

from hpotk.annotations import HpoDiseases, EvidenceCode, AnnotationReference, Sex
from hpotk.annotations import SimpleHpoDiseaseAnnotation, SimpleHpoDisease, SimpleHpoDiseases, SimpleHpoClinicalCourseAnnotation
from hpotk.model import TermId
from hpotk.ontology import MinimalOntology
from hpotk.util import open_text_io_handle_for_reading
from hpotk.constants.hpo.frequency import parse_hpo_frequency
from hpotk.annotations.load._api import HpoDiseaseLoader


HpoAnnotationLine = namedtuple('HpoAnnotationLine',
                               field_names=[
                                   'disease_id', 'disease_name', 'is_negated',
                                   'phenotype_term_id',
                                   'annotation_references', 'onset', 'frequency',
                                   'sex', 'modifiers', 'aspect', 'curators']
                               )

HPOA_VERSION_PATTERN = re.compile(r'^#(date|version): (?P<version>[\w-]+)\w?$')
HPO_PATTERN = re.compile(r'^HP:\d{7}$')
RATIO_PATTERN = re.compile(r'^(?P<numerator>\d+)/(?P<denominator>\d+)$')
PERCENTAGE_PATTERN = re.compile(r'^(?P<value>\d+\.?(\d+)?)%$')


class Ratio:
    """
    A private helper class for parsing frequency data.
    """

    def __init__(self, numerator: int, denominator: int):
        self._numerator = numerator
        self._denominator = denominator

    @property
    def numerator(self) -> int:
        return self._numerator

    @property
    def denominator(self) -> int:
        return self._denominator

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
            return Ratio(left.numerator + right.numerator, left.denominator + right.denominator)
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

    def __repr__(self):
        return f"SimpleRatio(" \
               f"numerator={self._numerator}, " \
               f"denominator={self._denominator})"


class SimpleHpoaDiseaseLoader(HpoDiseaseLoader):
    """
    Loads HPO annotation file into :class:`HpoDiseases`.
    """

    def __init__(self, hpo: MinimalOntology,
                 cohort_size: int = 50,
                 salvage_negated_frequencies: bool = False):
        if not isinstance(hpo, MinimalOntology):
            raise ValueError(f'hpo must be an instance of `MinimalOntology` but was {type(hpo)}')
        self._hpo = hpo
        self._cohort_size = cohort_size
        self._salvage_negated_frequencies = salvage_negated_frequencies

    def load(self, file: typing.Union[typing.IO, str]) -> HpoDiseases:
        data: typing.Mapping[str, typing.List[HpoAnnotationLine]] = defaultdict(list)
        version = None
        expecting_to_see_header_line = True
        with open_text_io_handle_for_reading(file) as fh:
            for line in fh:
                if expecting_to_see_header_line:
                    if line.startswith('#'):
                        # header
                        if line.startswith('#DatabaseID'):
                            # The older HPOA format
                            expecting_to_see_header_line = False
                        else:
                            version_matcher = HPOA_VERSION_PATTERN.match(line)
                            if version_matcher:
                                version = version_matcher.group('version')
                    else:
                        if line.startswith('database_id'):
                            expecting_to_see_header_line = False
                    continue
                else:
                    # corpus
                    hpoa = _parse_hpoa_line(line)
                    if hpoa:
                        data[hpoa.disease_id].append(hpoa)

        diseases = []
        for disease_id, hpoa_lines in data.items():
            disease = self._assemble_hpo_disease(disease_id, hpoa_lines)
            diseases.append(disease)

        return SimpleHpoDiseases(diseases, version)

    @property
    def cohort_size(self) -> int:
        return self._cohort_size

    def _assemble_hpo_disease(self, disease_curie: str, hpoa_lines: typing.List[HpoAnnotationLine]):
        # If the hpoa_lines is empty, then there is something wrong with the `defaultdict` and the logic above.
        disease_id = TermId.from_curie(disease_curie)
        disease_name = hpoa_lines[0].disease_name
        annotations, moi, onsets = self._parse_hpo_annotations(hpoa_lines)
        return SimpleHpoDisease(disease_id, disease_name, annotations, moi, onsets)

    def _parse_hpo_annotations(self, hpoa_lines: typing.Iterable[HpoAnnotationLine]) \
            -> typing.Tuple[typing.List[SimpleHpoDiseaseAnnotation], typing.Collection[TermId], typing.Collection[TermId]]:

        line_by_phenotype: typing.Mapping[str, typing.List[HpoAnnotationLine]] = defaultdict(list)
        line_by_clinical_course: typing.Mapping[str, typing.List[HpoAnnotationLine]] = defaultdict(list)

        moi = set()
        for hpoa in hpoa_lines:
            if hpoa.aspect == Aspect.PHENOTYPE:
                # Several HPOA lines may correspond to a single phenotype feature
                line_by_phenotype[hpoa.phenotype_term_id].append(hpoa)
            elif hpoa.aspect == Aspect.INHERITANCE:
                moi.add(hpoa.phenotype_term_id)
            elif hpoa.aspect == Aspect.C:
                line_by_clinical_course[hpoa.phenotype_term_id].append(hpoa)
                # TODO - handle the remaining aspect lines
                pass

        annotations = []
        for phenotype_curie, lines in line_by_phenotype.items():
            phenotype_id = TermId.from_curie(phenotype_curie)
            total_ratio = None
            annotation_references = set()
            modifiers = set()
            for line in lines:
                ratio = self._parse_frequency(line.is_negated, line.frequency)
                if total_ratio:
                    total_ratio = Ratio.fold(total_ratio, ratio)
                else:
                    total_ratio = ratio

                annotation_references.update(line.annotation_references)
                modifiers.update(line.modifiers)

            ann = SimpleHpoDiseaseAnnotation(phenotype_id,
                                             numerator=total_ratio.numerator,
                                             denominator=total_ratio.denominator,
                                             references=tuple(annotation_references),
                                             modifiers=tuple(modifiers))
            annotations.append(ann)

        onsets = []
        # TODO: other clinical course types
        for clinical_course_curie, lines in line_by_clinical_course.items():
            clinical_course_id = TermId.from_curie(clinical_course_curie)
            total_ratio = None
            annotation_references = set()
            modifiers = set()
            for line in lines:
                ratio = self._parse_frequency(line.is_negated, line.frequency)
                if total_ratio:
                    total_ratio = Ratio.fold(total_ratio, ratio)
                else:
                    total_ratio = ratio

                annotation_references.update(line.annotation_references)
                modifiers.update(line.modifiers)

            temporal_annotation = SimpleHpoClinicalCourseAnnotation(clinical_course_id,
                                         numerator=total_ratio.numerator,
                                         denominator=total_ratio.denominator,
                                         references=tuple(annotation_references),
                                         modifiers=tuple(modifiers))
            if temporal_annotation.type == "onset":
                onsets.append(temporal_annotation)
            else:
                pass


        return annotations, moi, onsets

    def _parse_frequency(self, is_negated: bool, frequency: str) -> Ratio:
        # An empty string is assumed to represent a case study
        if not frequency:
            numerator = 0 if is_negated else 1
            denominator = 1
            return Ratio(numerator, denominator)

        # HPO term, e.g. HP:0040280 (Obligate)
        hpo_match = HPO_PATTERN.match(frequency)
        if hpo_match:
            hpo_frequency = parse_hpo_frequency(frequency)
            numerator = 0 if is_negated else round(hpo_frequency.frequency * self._cohort_size)
            denominator = self._cohort_size
            return Ratio(numerator, denominator)

        # Ratio, e.g. 1/2
        ratio_match = RATIO_PATTERN.match(frequency)
        if ratio_match:
            denominator = int(ratio_match.group('denominator'))
            i = int(ratio_match.group('numerator'))
            if is_negated:
                if denominator == 0:
                    # fix denominator in cases like 0/0
                    denominator = self._cohort_size
                if i == 0 and self._salvage_negated_frequencies:
                    numerator = 0
                else:
                    numerator = denominator - i
            else:
                numerator = i

            return Ratio(numerator, denominator)

        # Percentage, e.g. 20%
        percentage_match = PERCENTAGE_PATTERN.match(frequency)
        if percentage_match:
            percentage = float(percentage_match.group('value'))
            numerator = round(percentage * self._cohort_size / 100)
            denominator = self._cohort_size
            return Ratio(numerator, denominator)

        raise ValueError(f'Unable to parse frequency {frequency}')


def _parse_hpoa_line(line: str) -> typing.Optional[HpoAnnotationLine]:
    fields = line.strip().split('\t')

    disease_id = fields[0]
    disease_name = fields[1]
    is_negated = fields[2].upper() == 'NOT'
    phenotype_id = fields[3]
    evidence_code = EvidenceCode.parse(fields[5])
    annotation_references = [AnnotationReference(TermId.from_curie(term_id), evidence_code)
                             for term_id
                             in filter(lambda t: t and not t.isspace(), fields[4].split(';'))]
    # TODO - implement parsing of temporal data
    onset = None

    frequency = fields[7]
    sex = Sex.parse(fields[8])

    modifiers = [TermId.from_curie(term_id)
                 for term_id
                 in filter(lambda t: t and not t.isspace(), fields[9].split(';'))]
    aspect = Aspect.parse(fields[10])
    curators = [curator.strip() for curator in fields[11].split(';')]

    return HpoAnnotationLine(disease_id, disease_name, is_negated,
                             phenotype_id,
                             annotation_references, onset, frequency,
                             sex, modifiers, aspect, curators)


class Aspect(enum.Enum):
    """Phenotype."""
    PHENOTYPE = 0
    """Inheritance."""
    INHERITANCE = 1
    """C"""
    C = 2
    """Modifier."""
    MODIFIER = 3

    @staticmethod
    def parse(value: str):
        """
        Parse :class:`Aspect` from `str` value.

        :param value: a `str` with the aspect code.
        :return: the parsed enum member or `None` if `value` is not valid :class:`Aspect` value.
        """
        value = value.upper()
        if value == 'P':
            return Aspect.PHENOTYPE
        elif value == 'I':
            return Aspect.INHERITANCE
        elif value == 'C':
            return Aspect.C
        elif value == 'M':
            return Aspect.MODIFIER
        else:
            return None
