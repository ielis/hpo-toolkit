import pytest

from ._impl import Aspect


class TestAspect:
    @pytest.mark.parametrize(
        "payload, expected",
        [
            (
                "P",
                Aspect.PHENOTYPE,
            ),
            (
                "H",
                Aspect.PAST_MEDICAL_HISTORY,
            ),
            (
                "I",
                Aspect.INHERITANCE,
            ),
            (
                "C",
                Aspect.ONSET_AND_CLINICAL_COURSE,
            ),
            (
                "M",
                Aspect.MODIFIER,
            ),
        ],
    )
    def test_parse(
        self,
        payload: str,
        expected: Aspect,
    ):
        actual = Aspect.parse(payload)

        assert actual == expected

    def test_parse_pony(self):
        assert Aspect.parse("Pony") is None
