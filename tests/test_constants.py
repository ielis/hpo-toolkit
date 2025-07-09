import pytest

import hpotk
from hpotk.constants.hpo.base import PHENOTYPIC_ABNORMALITY, MODE_OF_INHERITANCE
from hpotk.constants.hpo.frequency import parse_hpo_frequency
from hpotk.constants.hpo.frequency import (
    EXCLUDED,
    VERY_RARE,
    OCCASIONAL,
    FREQUENT,
    VERY_FREQUENT,
    OBLIGATE,
)


class TestHpoBase:
    def test_phenotypic_abnormality(self):
        assert PHENOTYPIC_ABNORMALITY.value == "HP:0000118"

    def test_mode_of_inheritance(self):
        assert MODE_OF_INHERITANCE.value == "HP:0000005"


class TestHpoFrequency:
    def test_term_ids(self):
        assert EXCLUDED.value == "HP:0040285"
        assert VERY_RARE.value == "HP:0040284"
        assert OCCASIONAL.value == "HP:0040283"
        assert FREQUENT.value == "HP:0040282"
        assert VERY_FREQUENT.value == "HP:0040281"
        assert OBLIGATE.value == "HP:0040280"

    @pytest.mark.parametrize(
        "term_id,frequency",
        [
            (EXCLUDED, 0.0),
            (VERY_RARE, 0.025),
            (OCCASIONAL, 0.16999999999),
            (FREQUENT, 0.545),
            (VERY_FREQUENT, 0.895),
            (OBLIGATE, 1.0),
        ],
    )
    def test_frequency(
        self,
        term_id: hpotk.TermId,
        frequency: float,
    ):
        hpo_frequency = parse_hpo_frequency(term_id)

        assert hpo_frequency is not None
        assert hpo_frequency.frequency == pytest.approx(frequency)
