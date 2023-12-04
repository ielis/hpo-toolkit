import os

import pytest
from pkg_resources import resource_filename

import hpotk
from hpotk import TermId

TOY_HPO = resource_filename(__name__, os.path.join('data', 'hp.toy.json'))

hpotk.util.setup_logging()


class TestTerms:
    """
    We only load the ontology once, and we test the properties of the loaded data.
    """

    @pytest.fixture(scope='class')
    def toy_hpo(self) -> hpotk.Ontology:
        return hpotk.load_ontology(TOY_HPO)

    def test_term_properties(self, toy_hpo: hpotk.Ontology):
        # Test properties of a Term
        term = toy_hpo.get_term('HP:0001626')

        assert term.identifier.value == 'HP:0001626'
        assert term.name == 'Abnormality of the cardiovascular system'
        assert term.definition == 'Any abnormality of the cardiovascular system.'
        assert term.comment == 'The cardiovascular system consists of the heart, vasculature, and the lymphatic system.'
        assert not term.is_obsolete
        assert term.alt_term_ids == (TermId.from_curie('HP:0003116'),)

        synonyms = term.synonyms
        assert len(synonyms) == 3

        one = synonyms[0]
        assert one.name == 'Cardiovascular disease'
        assert one.category == hpotk.model.SynonymCategory.RELATED
        assert one.synonym_type == hpotk.model.SynonymType.LAYPERSON_TERM
        assert one.xrefs is None

        two = synonyms[1]
        assert two.name == 'Cardiovascular abnormality'
        assert two.category == hpotk.model.SynonymCategory.EXACT
        assert two.synonym_type == hpotk.model.SynonymType.LAYPERSON_TERM
        assert two.xrefs is None

        three = synonyms[2]
        assert three.name == 'Abnormality of the cardiovascular system'
        assert three.category == hpotk.model.SynonymCategory.EXACT
        assert three.synonym_type == hpotk.model.SynonymType.LAYPERSON_TERM
        assert three.xrefs is None

        assert term.xrefs == tuple(
            TermId.from_curie(curie) for curie in
            ('UMLS:C0243050', 'UMLS:C0007222', 'MSH:D018376', 'SNOMEDCT_US:49601007', 'MSH:D002318')
        )

    def test_synonym_properties(self, toy_hpo: hpotk.Ontology):
        term = toy_hpo.get_term('HP:0001627')

        synonym = term.synonyms[7]

        assert synonym.name == 'Abnormally shaped heart'
        assert synonym.category == hpotk.model.SynonymCategory.EXACT
        assert synonym.synonym_type == hpotk.model.SynonymType.LAYPERSON_TERM
        assert synonym.xrefs == [TermId.from_curie('ORCID:0000-0001-5208-3432')]
