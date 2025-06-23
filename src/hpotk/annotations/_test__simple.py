import pytest

from hpotk.model import TermId

from ._simple import SimpleHpoDiseaseAnnotation


class TestSimpleHpoAnnotation:
    @pytest.mark.parametrize(
        "numerator,denominator,msg",
        [
            (-1, 1, "Numerator -1 must be a non-negative `int`"),
            (1, 0, "Denominator 0 must be a positive `int`"),
            (1, -1, "Denominator -1 must be a positive `int`"),
        ],
    )
    def test_errors(self, numerator, denominator, msg):
        tid = TermId.from_curie("HP:1234567")
        with pytest.raises(ValueError) as eh:
            SimpleHpoDiseaseAnnotation(tid, numerator, denominator, {}, (), ())

        assert eh.value.args == (msg,)
