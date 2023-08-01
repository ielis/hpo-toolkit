import unittest
import ddt

from hpotk.model import TermId

from ._simple import SimpleHpoDiseaseAnnotation


@ddt.ddt
class TestSimpleHpoAnnotation(unittest.TestCase):

    @ddt.unpack
    @ddt.data(
        [-1,  1, "Numerator -1 must be a non-negative `int`"],
        [1,  0, "Denominator 0 must be a positive `int`"],
        [1, -1, "Denominator -1 must be a positive `int`"],
    )
    def test_errors(self, numerator, denominator, msg):
        tid = TermId.from_curie('HP:1234567')
        with self.assertRaises(ValueError) as eh:
            SimpleHpoDiseaseAnnotation(tid, numerator, denominator, (), ())

        self.assertEqual(eh.exception.args[0], msg)
