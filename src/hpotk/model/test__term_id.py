import unittest

import ddt

from ._term_id import *


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


