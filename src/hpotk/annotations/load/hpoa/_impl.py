import logging
import re
import enum
import typing
from collections import defaultdict, namedtuple

from hpotk.annotations import HpoDiseases, EvidenceCode, AnnotationReference, Sex
from hpotk.model import TermId
from hpotk.ontology import MinimalOntology
from hpotk.util import open_text_io_handle_for_reading
from hpotk.constants.hpo.frequency import parse_hpo_frequency
from hpotk.constants.hpo.onset import ALL_ONSETS, ONSET
from hpotk.annotations.load._api import HpoDiseaseLoader

from ..._simple import (
    SimpleHpoDiseaseAnnotation,
    SimpleHpoDisease,
    SimpleHpoDiseases,
)

HpoAnnotationLine = namedtuple(
    "HpoAnnotationLine",
    field_names=[
        "disease_id",
        "disease_name",
        "is_negated",
        "phenotype_term_id",
        "annotation_references",
        "onset",
        "frequency",
        "sex",
        "modifiers",
        "aspect",
        "curators",
    ],
)

HPOA_VERSION_PATTERN = re.compile(r"^#(date|version): (?P<version>[\w-]+)\w?$")
HPO_PATTERN = re.compile(r"^HP:\d{7}$")
RATIO_PATTERN = re.compile(r"^(?P<numerator>\d+)/(?P<denominator>\d+)$")
PERCENTAGE_PATTERN = re.compile(r"^(?P<value>\d+\.?(\d+)?)%$")


class Ratio:
    def __init__(self):
        self.numerator = 0
        self.denominator = 0

    def merge(
        self,
        numerator: int,
        denominator: int,
    ):
        self.numerator += numerator
        self.denominator += denominator


class SimpleHpoaDiseaseLoader(HpoDiseaseLoader):
    """
    Loads HPO annotation file into :class:`HpoDiseases`.

    Any issues are reported via logger.
    """

    def __init__(
        self,
        hpo: MinimalOntology,
        cohort_size: int = 50,
        salvage_negated_frequencies: bool = False,
    ):
        if not isinstance(hpo, MinimalOntology):
            raise ValueError(
                f"hpo must be an instance of `MinimalOntology` but was {type(hpo)}"
            )
        self._hpo = hpo
        self._logger = logging.getLogger(__name__)
        self._cohort_size = cohort_size
        self._salvage_negated_frequencies = salvage_negated_frequencies

    def load(
        self,
        file: typing.Union[typing.IO, str],
    ) -> HpoDiseases:
        data: typing.Mapping[str, typing.List[HpoAnnotationLine]] = defaultdict(list)
        version = None
        expecting_to_see_header_line = True
        with open_text_io_handle_for_reading(file) as fh:
            for line in fh:
                if expecting_to_see_header_line:
                    if line.startswith("#"):
                        # header
                        if line.startswith("#DatabaseID"):
                            # The older HPOA format
                            expecting_to_see_header_line = False
                        else:
                            version_matcher = HPOA_VERSION_PATTERN.match(line)
                            if version_matcher:
                                version = version_matcher.group("version")
                    else:
                        if line.startswith("database_id"):
                            expecting_to_see_header_line = False
                    continue
                else:
                    # corpus
                    hpoa, err = _parse_hpoa_line(line)
                    if hpoa is None:
                        self._logger.warning("%s in line `%s`", err, line)
                    else:
                        data[hpoa.disease_id].append(hpoa)

        diseases = []
        for disease_id, hpoa_lines in data.items():
            disease = self._assemble_hpo_disease(disease_id, hpoa_lines)
            diseases.append(disease)

        return SimpleHpoDiseases(diseases, version)

    @property
    def cohort_size(self) -> int:
        return self._cohort_size

    def _assemble_hpo_disease(
        self,
        disease_curie: str,
        hpoa_lines: typing.Sequence[HpoAnnotationLine],
    ):
        # If the hpoa_lines is empty, then there is something wrong with the `defaultdict` and the logic above.
        disease_id = TermId.from_curie(disease_curie)
        disease_name = hpoa_lines[0].disease_name
        annotations, moi, onsets = self._parse_hpo_annotations(hpoa_lines)
        return SimpleHpoDisease(disease_id, disease_name, annotations, moi, onsets)

    def _parse_hpo_annotations(
        self,
        hpoa_lines: typing.Iterable[HpoAnnotationLine],
    ) -> typing.Tuple[
        typing.Sequence[SimpleHpoDiseaseAnnotation],
        typing.Collection[TermId],
        typing.Collection[TermId],
    ]:
        line_by_phenotype: typing.Mapping[str, typing.List[HpoAnnotationLine]] = (
            defaultdict(list)
        )

        moi = set()
        onsets = set()
        for hpoa in hpoa_lines:
            if hpoa.aspect == Aspect.PHENOTYPE:
                # Several HPOA lines may correspond to a single phenotype feature
                line_by_phenotype[hpoa.phenotype_term_id].append(hpoa)
            elif hpoa.aspect == Aspect.INHERITANCE:
                moi.add(TermId.from_curie(hpoa.phenotype_term_id))
            elif hpoa.aspect == Aspect.ONSET_AND_CLINICAL_COURSE:
                term_id = TermId.from_curie(hpoa.phenotype_term_id)
                if term_id in ALL_ONSETS:
                    onsets.add(term_id)
            else:
                # TODO - handle the remaining aspect lines
                pass

        annotations = []
        for phenotype_curie, lines in line_by_phenotype.items():
            assert len(lines) != 0, "We must have at least one HPOA line for a CURIE"

            phenotype_id = TermId.from_curie(phenotype_curie)
            total_numerator, total_denominator = 0, 0
            feature_onsets = defaultdict(Ratio)
            annotation_references = set()
            modifiers = set()
            for line in lines:
                numerator, denominator = self._parse_frequency(
                    line.is_negated, line.frequency
                )
                total_numerator += numerator
                total_denominator += denominator

                if len(line.onset) != 0:
                    onset = self._parse_onset(line.onset)
                    if onset is None:
                        self._logger.warning(
                            "Unable to interpret onset %s in line %s",
                            line.onset,
                            "\t".join(
                                (
                                    line.disease_id,
                                    line.disease_name,
                                    line.phenotype_term_id,
                                )
                            ),
                        )
                    else:
                        feature_onsets[onset].merge(numerator, denominator)
                        for anc in self._hpo.graph.get_ancestors(onset):
                            if anc == ONSET:
                                break
                            feature_onsets[anc].merge(numerator, denominator)

                annotation_references.update(line.annotation_references)
                modifiers.update(line.modifiers)

            ann = SimpleHpoDiseaseAnnotation(
                phenotype_id,
                numerator=total_numerator,
                denominator=total_denominator,
                onsets=((onset, (ratio.numerator, ratio.denominator)) for onset, ratio in feature_onsets.items()),
                references=annotation_references,
                modifiers=modifiers,
            )
            annotations.append(ann)

        return annotations, moi, onsets

    def _parse_frequency(
        self,
        is_negated: bool,
        frequency: str,
    ) -> typing.Tuple[int, int]:
        # An empty string is assumed to represent a case study
        if not frequency:
            numerator = 0 if is_negated else 1
            denominator = 1
            return numerator, denominator

        # HPO term, e.g. HP:0040280 (Obligate)
        hpo_match = HPO_PATTERN.match(frequency)
        if hpo_match:
            hpo_frequency = parse_hpo_frequency(frequency)
            numerator = (
                0 if is_negated else round(hpo_frequency.frequency * self._cohort_size)
            )
            denominator = self._cohort_size
            return numerator, denominator

        # Ratio, e.g. 1/2
        ratio_match = RATIO_PATTERN.match(frequency)
        if ratio_match:
            denominator = int(ratio_match.group("denominator"))
            i = int(ratio_match.group("numerator"))
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

            return numerator, denominator

        # Percentage, e.g. 20%
        percentage_match = PERCENTAGE_PATTERN.match(frequency)
        if percentage_match:
            percentage = float(percentage_match.group("value"))
            numerator = round(percentage * self._cohort_size / 100)
            denominator = self._cohort_size
            return numerator, denominator

        raise ValueError(f"Unable to parse frequency {frequency}")

    def _parse_onset(
        self,
        onset: str,
    ) -> typing.Optional[TermId]:
        match = HPO_PATTERN.match(onset)
        if match:
            term_id = TermId.from_curie(onset)
            if self._hpo.graph.is_ancestor_of(ONSET, term_id):
                return term_id

        return None


def _parse_hpoa_line(
    line: str,
) -> typing.Tuple[
    typing.Optional[HpoAnnotationLine],
    typing.Optional[str],
]:
    fields = line.strip().split("\t")

    if len(fields) < 12:
        return None, f"Found less than 12 fields ({len(fields)})"

    disease_id = fields[0]
    disease_name = fields[1]
    is_negated = fields[2].upper() == "NOT"
    phenotype_id = fields[3]
    evidence_code = EvidenceCode.parse(fields[5])
    if evidence_code is None:
        return None, f"Invalid evidence code `{fields[5]}`"
    annotation_references = [
        AnnotationReference(TermId.from_curie(term_id), evidence_code)
        for term_id in filter(lambda t: t and not t.isspace(), fields[4].split(";"))
    ]
    onset = fields[6]

    frequency = fields[7]
    sex = Sex.parse(fields[8])

    modifiers = [
        TermId.from_curie(term_id)
        for term_id in filter(lambda t: t and not t.isspace(), fields[9].split(";"))
    ]
    aspect = Aspect.parse(fields[10])
    curators = [curator.strip() for curator in fields[11].split(";")]

    return (
        HpoAnnotationLine(
            disease_id,
            disease_name,
            is_negated,
            phenotype_id,
            annotation_references,
            onset,
            frequency,
            sex,
            modifiers,
            aspect,
            curators,
        ),
        None,
    )


class Aspect(enum.Enum):
    """
    An enum for the aspect column of the HPO annotation lines.
    """

    PHENOTYPE = 0
    """
    Phenotype.
    """
    INHERITANCE = 1
    """
    Inheritance.
    """
    ONSET_AND_CLINICAL_COURSE = 2
    """
    Onset and clinical course.
    """
    MODIFIER = 3
    """
    Modifier.
    """
    PAST_MEDICAL_HISTORY = 4
    """
    Past medical history.
    """

    @staticmethod
    def parse(
        value: str,
    ) -> typing.Optional["Aspect"]:
        """
        Parse :class:`Aspect` from `str` value.

        :param value: a `str` with the aspect code.
        :return: the parsed enum member or `None` if `value` is not valid :class:`Aspect` value.
        """
        value = value.upper()
        if value == "P":
            return Aspect.PHENOTYPE
        elif value == "C":
            return Aspect.ONSET_AND_CLINICAL_COURSE
        elif value == "I":
            return Aspect.INHERITANCE
        elif value == "M":
            return Aspect.MODIFIER
        elif value == "H":
            return Aspect.PAST_MEDICAL_HISTORY
        else:
            return None
