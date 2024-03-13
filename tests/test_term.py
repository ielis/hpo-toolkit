from hpotk.model import *


class TestMinimalTerm:

    def test_equal_terms_are_equal(self):
        one = MinimalTerm.create_minimal_term(TermId.from_curie("HP:1234567"),
                                              "First",
                                              [TermId.from_curie("HP:1111111")],
                                              False)
        other = MinimalTerm.create_minimal_term(TermId.from_curie("HP:1234567"),
                                                "First",
                                                [TermId.from_curie("HP:1111111")],
                                                False)
        assert one == other

    def test_unequal_terms_are_not_equal(self):
        one = MinimalTerm.create_minimal_term(TermId.from_curie("HP:1234567"),
                                              "First",
                                              [TermId.from_curie("HP:1111111")],
                                              False)
        other = MinimalTerm.create_minimal_term(TermId.from_curie("HP:1234567"),
                                                "Second",
                                                [TermId.from_curie("HP:1111111")],
                                                False)
        assert one != other


class TestTerm:

    def test_equal_terms_are_equal(self):
        one_id = TermId.from_curie("HP:1234567")
        one_syn = Synonym('F', SynonymCategory.EXACT, None, [TermId.from_curie('ORCID:1234-5678-1234-5678')])
        one = Term.create_term(identifier=one_id,
                               name="First",
                               alt_term_ids=[TermId.from_curie("HP:1111111")],
                               is_obsolete=False,
                               definition="First term definition",
                               comment="First comment",
                               synonyms=[one_syn], xrefs=[TermId.from_curie("SNOMED_CT:123456")])
        two_id = TermId.from_curie("HP:1234567")
        two = Term.create_term(identifier=two_id,
                               name="First",
                               alt_term_ids=[TermId.from_curie("HP:1111111")],
                               is_obsolete=False,
                               definition=Definition("First term definition", ()),
                               comment="First comment",
                               synonyms=[one_syn], xrefs=[TermId.from_curie("SNOMED_CT:123456")])
        assert one == two

    def test_not_equal_terms_are_not_equal(self):
        one_id = TermId.from_curie("HP:1111111")
        one = Term.create_term(identifier=one_id,
                               name="First",
                               alt_term_ids=[TermId.from_curie("HP:2222222")],
                               is_obsolete=False,
                               definition="First term definition",
                               comment="Other comment",
                               synonyms=None,
                               xrefs=None)
        two_id = TermId.from_curie("HP:1111111")
        two = Term.create_term(identifier=two_id,
                               name="First",
                               alt_term_ids=[TermId.from_curie("HP:2222222")],
                               is_obsolete=False,
                               definition="First term definition",
                               comment="First comment",
                               synonyms=None,
                               xrefs=None)
        assert one != two

    def test_current_obsolete_synonyms(self):
        current_one = Synonym('A', SynonymCategory.EXACT, SynonymType.LAYPERSON_TERM, None)
        current_two = Synonym('B', SynonymCategory.EXACT, SynonymType.LAYPERSON_TERM, None)
        obsolete_two = Synonym('C', SynonymCategory.EXACT, SynonymType.OBSOLETE_SYNONYM, None)
        term = Term.create_term(identifier=TermId.from_curie('HP:1111111'),
                                name="First",
                                alt_term_ids=[TermId.from_curie("HP:2222222")],
                                is_obsolete=False,
                                definition="First term definition",
                                comment="Other comment",
                                synonyms=[current_one, current_two, obsolete_two],
                                xrefs=None)

        current = list(map(lambda s: s.name, term.current_synonyms()))
        assert current == ['A', 'B']
        obsolete = list(map(lambda s: s.name, term.obsolete_synonyms()))
        assert obsolete == ['C']
