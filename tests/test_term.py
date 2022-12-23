import unittest

from hpotk.model import *


class TestMinimalTerm(unittest.TestCase):

    def test_equal_terms_are_equal(self):
        one = MinimalTerm.create_minimal_term(TermId.from_curie("HP:1234567"),
                                              "First",
                                              [TermId.from_curie("HP:1111111")],
                                              False)
        other = MinimalTerm.create_minimal_term(TermId.from_curie("HP:1234567"),
                                                "First",
                                                [TermId.from_curie("HP:1111111")],
                                                False)
        self.assertEqual(one, other)

    def test_unequal_terms_are_not_equal(self):
        one = MinimalTerm.create_minimal_term(TermId.from_curie("HP:1234567"),
                                              "First",
                                              [TermId.from_curie("HP:1111111")],
                                              False)
        other = MinimalTerm.create_minimal_term(TermId.from_curie("HP:1234567"),
                                                "Second",
                                                [TermId.from_curie("HP:1111111")],
                                                False)
        self.assertNotEqual(one, other)


class TestTerm(unittest.TestCase):

    def test_equal_terms_are_equal(self):
        one_id = TermId.from_curie("HP:1234567")
        one = Term.create_term(identifier=one_id,
                               name="First",
                               alt_term_ids=[TermId.from_curie("HP:1111111")],
                               is_obsolete=False,
                               definition="First term definition",
                               comment="First comment")
        two_id = TermId.from_curie("HP:1234567")
        two = Term.create_term(identifier=two_id,
                               name="First",
                               alt_term_ids=[TermId.from_curie("HP:1111111")],
                               is_obsolete=False,
                               definition="First term definition",
                               comment="First comment")
        self.assertEqual(one, two)

    def test_not_equal_terms_are_not_equal(self):
        one_id = TermId.from_curie("HP:1111111")
        one = Term.create_term(identifier=one_id,
                               name="First",
                               alt_term_ids=[TermId.from_curie("HP:2222222")],
                               is_obsolete=False,
                               definition="First term definition",
                               comment="Other comment")
        two_id = TermId.from_curie("HP:1111111")
        two = Term.create_term(identifier=two_id,
                               name="First",
                               alt_term_ids=[TermId.from_curie("HP:2222222")],
                               is_obsolete=False,
                               definition="First term definition",
                               comment="First comment")
        self.assertNotEqual(one, two)
