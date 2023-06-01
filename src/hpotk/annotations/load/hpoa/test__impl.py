
import unittest
import ddt

from ._impl import Ratio


@ddt.ddt
class TestRatio(unittest.TestCase):

    def test_positive(self):
        ratio = Ratio(1, 4)
        self.assertEqual(ratio.numerator, 1)
        self.assertEqual(ratio.denominator, 4)
        self.assertAlmostEqual(ratio.frequency, 1/4)
        self.assertTrue(ratio.is_positive())
        self.assertFalse(ratio.is_zero())

    def test_zero(self):
        ratio = Ratio(0, 1)
        self.assertEqual(ratio.numerator, 0)
        self.assertEqual(ratio.denominator, 1)
        self.assertAlmostEqual(ratio.frequency, 0.)
        self.assertFalse(ratio.is_positive())
        self.assertTrue(ratio.is_zero())

    @ddt.unpack
    @ddt.data(
        [1, 1, 2, 2, True],
        [1, 4, 2, 8, True],
        [2, 8, 1, 4, True],

        [1, 4, 3, 8, False],
        [1, 8, 1, 4, False],
    )
    def test_equality(self, left_num, left_denom, right_num, right_denom, expected):
        left = Ratio(left_num, left_denom)
        right = Ratio(right_num, right_denom)
        self.assertEqual(left == right, expected)

    @ddt.unpack
    @ddt.data(
        [1, 1, 2, 2, 3, 3],
        [1, 2, 3, 4, 4, 6],
    )
    def test_fold(self, left_num, left_denom, right_num, right_denom, result_num, result_denom):
        left = Ratio(left_num, left_denom)
        right = Ratio(right_num, right_denom)

        result = Ratio.fold(left, right)

        self.assertEqual(result.numerator, result_num)
        self.assertEqual(result.denominator, result_denom)

