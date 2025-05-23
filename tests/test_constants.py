class TestHpoBase:
    def test_phenotypic_abnormality(self):
        from hpotk.constants.hpo.base import PHENOTYPIC_ABNORMALITY

        assert PHENOTYPIC_ABNORMALITY.value == "HP:0000118"

    def test_mode_of_inheritance(self):
        from hpotk.constants.hpo.base import MODE_OF_INHERITANCE

        assert MODE_OF_INHERITANCE.value == "HP:0000005"


class TestHpoFrequency:
    def test_frequencies(self):
        from hpotk.constants.hpo.frequency import (
            EXCLUDED,
            VERY_RARE,
            OCCASIONAL,
            FREQUENT,
            VERY_FREQUENT,
            OBLIGATE,
        )

        assert EXCLUDED.value == "HP:0040285"
        assert VERY_RARE.value == "HP:0040284"
        assert OCCASIONAL.value == "HP:0040283"
        assert FREQUENT.value == "HP:0040282"
        assert VERY_FREQUENT.value == "HP:0040281"
        assert OBLIGATE.value == "HP:0040280"
