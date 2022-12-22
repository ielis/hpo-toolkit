import unittest

import ddt

from ._term_id import *


@ddt.ddt
class TestTermId(unittest.TestCase):

    @ddt.data("HP:1234567", "HP_1234567")
    def test_from_curie(self, curie):
        term_id = TermId.from_curie(curie)
        assert term_id.value == curie

    @ddt.unpack
    @ddt.data(
        ("HP1234567", "The CURIE HP1234567 has no colon `:` or underscore `_`"),
        (None, "Curie must not be None")
    )
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
        self.assertEqual(curie, term_id.value)

    def test_equality(self):
        first = TermId.from_curie("HP:1234567")
        second = TermId.from_curie("HP:1234567")
        self.assertEqual(first, second)


