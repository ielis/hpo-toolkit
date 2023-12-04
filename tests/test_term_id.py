import pytest

from hpotk.model import *


class TestTermId:

    @pytest.mark.parametrize('curie',
                             ("HP:1234567", "HP_1234567")
                             )
    def test_from_curie(self, curie):
        term_id = TermId.from_curie(curie)
        assert term_id.value == "HP:1234567"

    def test_from_curie__unusual_input(self):
        term_id = TermId.from_curie('SNOMEDCT_US:313307000')
        assert term_id.prefix == 'SNOMEDCT_US'
        assert term_id.id == '313307000'

    @pytest.mark.parametrize('curie, message',
                             (("HP1234567", "The CURIE HP1234567 has no colon `:` or underscore `_`"),
                              (None, "Curie must not be None"))
                             )
    def test_from_curie__failures(self, curie, message):
        with pytest.raises(ValueError) as cm:
            TermId.from_curie(curie)

        assert message == cm.value.args[0]

    @pytest.mark.parametrize('curie, prefix, id',
                             (
                                     ["HP:1234567", "HP", "1234567"],
                                     ["HP_1234567", "HP", "1234567"]
                             )
                             )
    def test_properties(self, curie, prefix, id):
        term_id = TermId.from_curie(curie)

        assert prefix == term_id.prefix
        assert id == term_id.id
        assert f'{prefix}:{id}' == term_id.value

    @pytest.mark.parametrize('left, right',
                             (["HP:1234567", "HP:1234567"],
                              ["HP:1234567", "HP_1234567"],
                              ["HP_1234567", "HP:1234567"],
                              ["HP_1234567", "HP_1234567"],)
                             )
    def test_equality(self, left, right):
        left = TermId.from_curie(left)
        right = TermId.from_curie(right)

        assert left == right

    @pytest.mark.parametrize('left, right, is_gt, is_eq, is_lt',
                             (
                                     # First compare by prefix
                                     ["AA:0000000", "BB:0000000", False, False, True],
                                     ["BB:0000000", "BB:0000000", False, True, False],
                                     ["CC:0000000", "BB:0000000", True, False, False],
                                     # Then by value
                                     ["HP:0000001", "HP:0000002", False, False, True],
                                     ["HP:0000002", "HP:0000002", False, True, False],
                                     ["HP:0000003", "HP:0000002", True, False, False],
                             )
                             )
    def test_comparison(self, left, right, is_gt, is_eq, is_lt):
        left = TermId.from_curie(left)
        right = TermId.from_curie(right)
        assert (left > right) == is_gt
        assert (left == right) == is_eq
        assert (left < right) == is_lt
