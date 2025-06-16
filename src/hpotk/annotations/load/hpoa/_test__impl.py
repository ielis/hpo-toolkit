import pytest

from ._impl import Ratio, Aspect


class TestRatio:
    def test_positive(self):
        ratio = Ratio(1, 4)
        assert ratio.numerator == 1
        assert ratio.denominator == 4
        assert ratio.frequency == 1 / 4
        assert ratio.is_positive()
        assert ratio.is_zero()

    def test_zero(self):
        ratio = Ratio(0, 1)
        assert ratio.numerator == 0
        assert ratio.denominator == 1
        assert ratio.frequency == 0.0
        assert ratio.is_positive()
        assert ratio.is_zero()

    @pytest.mark.parametrize(
        "left_num, left_denom, right_num, right_denom, expected",
        (
            [1, 1, 2, 2, True],
            [1, 4, 2, 8, True],
            [2, 8, 1, 4, True],
            [1, 4, 3, 8, False],
            [1, 8, 1, 4, False],
        ),
    )
    def test_equality(
        self,
        left_num: int,
        left_denom: int,
        right_num: int,
        right_denom: int,
        expected: bool,
    ):
        left = Ratio(left_num, left_denom)
        right = Ratio(right_num, right_denom)

        assert left == right == expected

    @pytest.mark.parametrize(
        "left_num, left_denom, right_num, right_denom, expected",
        (
            [1, 1, 2, 2, 3, 3],
            [1, 2, 3, 4, 4, 6],
        ),
    )
    def test_fold(
        self,
        left_num: int,
        left_denom: int,
        right_num: int,
        right_denom: int,
        result_num: int,
        result_denom: int,
    ):
        left = Ratio(left_num, left_denom)
        right = Ratio(right_num, right_denom)

        result = Ratio.fold(left, right)

        assert result.numerator == result_num
        assert result.denominator == result_denom


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
