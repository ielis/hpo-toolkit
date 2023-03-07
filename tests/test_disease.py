import unittest

import ddt

from hpotk.model.disease import Ratio, EvidenceCode


@ddt.ddt
class TestRatio(unittest.TestCase):

    def test_positive(self):
        ratio = Ratio.create(1, 4)
        self.assertEqual(ratio.numerator, 1)
        self.assertEqual(ratio.denominator, 4)
        self.assertAlmostEqual(ratio.frequency, 1/4)
        self.assertTrue(ratio.is_positive())
        self.assertFalse(ratio.is_zero())

    def test_zero(self):
        ratio = Ratio.create(0, 1)
        self.assertEqual(ratio.numerator, 0)
        self.assertEqual(ratio.denominator, 1)
        self.assertAlmostEqual(ratio.frequency, 0.)
        self.assertFalse(ratio.is_positive())
        self.assertTrue(ratio.is_zero())

    @ddt.unpack
    @ddt.data(
        [-1,  1, "Numerator -1 must be a non-negative `int`"],
        [1,  0, "Denominator 0 must be a positive `int`"],
        [1, -1, "Denominator -1 must be a positive `int`"],
    )
    def test_errors(self, numerator, denominator, msg):
        with self.assertRaises(ValueError) as eh:
            Ratio.create(numerator, denominator)

        self.assertEqual(eh.exception.args[0], msg)

    @ddt.unpack
    @ddt.data(
        [1, 1, 2, 2, True],
        [1, 4, 2, 8, True],
        [2, 8, 1, 4, True],

        [1, 4, 3, 8, False],
        [1, 8, 1, 4, False],
    )
    def test_equality(self, left_num, left_denom, right_num, right_denom, expected):
        left = Ratio.create(left_num, left_denom)
        right = Ratio.create(right_num, right_denom)
        self.assertEqual(left == right, expected)

    @ddt.unpack
    @ddt.data(
        [1, 1, 2, 2, 3, 3],
        [1, 2, 3, 4, 4, 6],
    )
    def test_fold(self, left_num, left_denom, right_num, right_denom, result_num, result_denom):
        left = Ratio.create(left_num, left_denom)
        right = Ratio.create(right_num, right_denom)

        result = Ratio.fold(left, right)

        self.assertEqual(result.numerator, result_num)
        self.assertEqual(result.denominator, result_denom)


@ddt.ddt
class TestEvidenceCode(unittest.TestCase):

    @ddt.unpack
    @ddt.data(
        ['IEA'],
        ['TAS'],
        ['PCS'],
    )
    def test_parse_ok(self, code):
        ec: EvidenceCode = EvidenceCode.parse(code)
        self.assertEqual(ec, EvidenceCode[code])

    def test_parse_error(self):
        ec = EvidenceCode.parse('GIBBERISH')
        self.assertIsNone(ec)
