import re
import enum
import typing
from collections import defaultdict, namedtuple

from hpotk.annotations import HpoDiseases, EvidenceCode, AnnotationReference, Sex, Ratio
from hpotk.annotations import SimpleHpoDiseaseAnnotation, SimpleHpoDisease, SimpleHpoDiseases
from hpotk.model import TermId
from hpotk.ontology import MinimalOntology
from hpotk.util import open_text_io_handle
from hpotk.constants.hpo.frequency import parse_hpo_frequency
from hpotk.annotations.load._api import HpoDiseaseLoader

HpoAnnotationLine = namedtuple('HpoAnnotationLine',
                               field_names=[
                                   'disease_id', 'disease_name', 'is_negated',
                                   'phenotype_term_id',
                                   'annotation_references', 'onset', 'frequency',
                                   'sex', 'modifiers', 'aspect', 'curators']
                               )

HPOA_VERSION_PATTERN = re.compile(r'^#date: (?P<version>[\w-]+)\w?$')
HPO_PATTERN = re.compile(r'^HP:\d{7}$')
RATIO_PATTERN = re.compile(r'^(?P<numerator>\d+)/(?P<denominator>\d+)$')
PERCENTAGE_PATTERN = re.compile(r'^(?P<value>\d+\.?(\d+)?)%$')


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
        data = defaultdict(list)
        version = None
        with open_text_io_handle(file) as fh:
            for line in fh:
                if line.startswith('#'):
                    # header
                    version_matcher = HPOA_VERSION_PATTERN.match(line)
                    if version_matcher:
                        version = version_matcher.group('version')
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

    def _assemble_hpo_disease(self, disease_id, hpoa_lines):
        # If the hpoa_lines is empty, then there is something wrong with the `defaultdict` and the logic above.
        disease_name = hpoa_lines[0].disease_name
        annotations, moi = self._parse_hpo_annotations(hpoa_lines)
        return SimpleHpoDisease(disease_id, disease_name, annotations, moi)

    def _parse_hpo_annotations(self, hpoa_lines: typing.Iterable[HpoAnnotationLine]) \
            -> typing.Tuple[typing.List[SimpleHpoDiseaseAnnotation], typing.Collection[TermId]]:

        line_by_phenotype = defaultdict(list)
        moi = set()
        for hpoa in hpoa_lines:
            if hpoa.aspect == Aspect.PHENOTYPE:
                # Several HPOA lines may correspond to a single phenotype feature
                line_by_phenotype[hpoa.phenotype_term_id].append(hpoa)
            elif hpoa.aspect == Aspect.INHERITANCE:
                moi.add(hpoa.phenotype_term_id)
            else:
                # TODO - handle the remaining aspect lines
                pass

        annotations = []
        for phenotype_term_id, lines in line_by_phenotype.items():
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

            ann = SimpleHpoDiseaseAnnotation(phenotype_term_id,
                                             total_ratio,
                                             list(annotation_references),
                                             list(modifiers))
            annotations.append(ann)

        return annotations, moi

    def _parse_frequency(self, is_negated: bool, frequency: str) -> Ratio:
        # An empty string is assumed to represent a case study
        if not frequency:
            numerator = 0 if is_negated else 1
            denominator = 1
            return Ratio.create(numerator, denominator)

        # HPO term, e.g. HP:0040280 (Obligate)
        hpo_match = HPO_PATTERN.match(frequency)
        if hpo_match:
            hpo_frequency = parse_hpo_frequency(frequency)
            numerator = 0 if is_negated else round(hpo_frequency.frequency * self._cohort_size)
            denominator = self._cohort_size
            return Ratio.create(numerator, denominator)

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

            return Ratio.create(numerator, denominator)

        # Percentage, e.g. 20%
        percentage_match = PERCENTAGE_PATTERN.match(frequency)
        if percentage_match:
            percentage = float(percentage_match.group('value'))
            numerator = round(percentage * self._cohort_size / 100)
            denominator = self._cohort_size
            return Ratio.create(numerator, denominator)

        raise ValueError(f'Unable to parse frequency {frequency}')


def _parse_hpoa_line(line: str) -> typing.Optional[HpoAnnotationLine]:
    fields = line.strip().split('\t')

    disease_id = TermId.from_curie(fields[0])
    disease_name = fields[1]
    is_negated = fields[2].upper() == 'NOT'
    phenotype_id = TermId.from_curie(fields[3])
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
