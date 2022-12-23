import unittest

import ddt

from hpotk.model import *


@ddt.ddt
class TestTermId(unittest.TestCase):

    @ddt.data("HP:1234567", "HP_1234567")
    def test_from_curie(self, curie):
        term_id = TermId.from_curie(curie)
        assert term_id.value == "HP:1234567"

    @ddt.data(
        ("HP1234567", "The CURIE HP1234567 has no colon `:` or underscore `_`"),
        (None, "Curie must not be None")
    )
    @ddt.unpack
    def test_from_curie__failures(self, curie, message):
        with self.assertRaises(ValueError) as cm:
            TermId.from_curie(curie)
        self.assertEqual(message, cm.exception.args[0])

    @ddt.unpack
    @ddt.data(
        ["HP:1234567", "HP", "1234567"],
        ["HP_1234567", "HP", "1234567"]
    )
    def test_properties(self, curie, prefix, id):
        term_id = TermId.from_curie(curie)
        self.assertEqual(prefix, term_id.prefix)
        self.assertEqual(id, term_id.id)
        self.assertEqual(f'{prefix}:{id}', term_id.value)

    @ddt.unpack
    @ddt.data(
        ["HP:1234567", "HP:1234567"],
        ["HP:1234567", "HP_1234567"],
        ["HP_1234567", "HP:1234567"],
        ["HP_1234567", "HP_1234567"],
    )
    def test_equality(self, left, right):
        left = TermId.from_curie(left)
        right = TermId.from_curie(right)
        self.assertEqual(left, right)

    @ddt.unpack
    @ddt.data(
        # First compare by prefix
        ["AA:0000000", "BB:0000000", False, False, True],
        ["BB:0000000", "BB:0000000", False, True, False],
        ["CC:0000000", "BB:0000000", True, False, False],
        # Then by value
        ["HP:0000001", "HP:0000002", False, False, True],
        ["HP:0000002", "HP:0000002", False, True, False],
        ["HP:0000003", "HP:0000002", True, False, False],
    )
    def test_comparison(self, left, right, is_gt, is_eq, is_lt):
        left = TermId.from_curie(left)
        right = TermId.from_curie(right)
        self.assertEqual(left > right, is_gt)
        self.assertEqual(left == right, is_eq)
        self.assertEqual(left < right, is_lt)
