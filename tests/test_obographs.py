import os
import unittest

from pkg_resources import resource_filename

import hpotk as hp
from hpotk.model import TermId
from hpotk.ontology.load.obographs import *

TOY_HPO = resource_filename(__name__, os.path.join('data', 'hp.toy.json'))

hp.util.setup_logging()


class TestTerms(unittest.TestCase):
    """
    We only load the ontology once, and we test the properties of the loaded data.
    """

    ONTOLOGY: hp.ontology.Ontology = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.ONTOLOGY = load_ontology(TOY_HPO)

    def test_term_properties(self):
        # Test properties of a Term
        term = TestTerms.ONTOLOGY.get_term('HP:0001626')

        self.assertEqual(term.identifier.value, 'HP:0001626')
        self.assertEqual(term.name, 'Abnormality of the cardiovascular system')
        self.assertEqual(term.definition, 'Any abnormality of the cardiovascular system.')
        self.assertEqual(term.comment, 'The cardiovascular system consists of the heart, vasculature, and the '
                                       'lymphatic system.')
        self.assertEqual(term.is_obsolete, False)
        self.assertListEqual(term.alt_term_ids, [TermId.from_curie('HP:0003116')])

        synonyms = term.synonyms
        self.assertEqual(len(synonyms), 3)

        one = synonyms[0]
        self.assertEqual(one.name, 'Cardiovascular disease')
        self.assertEqual(one.category, hp.model.SynonymCategory.RELATED)
        self.assertEqual(one.synonym_type, hp.model.SynonymType.LAYPERSON_TERM)
        self.assertIsNone(one.xrefs)

        two = synonyms[1]
        self.assertEqual(two.name, 'Cardiovascular abnormality')
        self.assertEqual(two.category, hp.model.SynonymCategory.EXACT)
        self.assertEqual(two.synonym_type, hp.model.SynonymType.LAYPERSON_TERM)
        self.assertIsNone(two.xrefs)

        three = synonyms[2]
        self.assertEqual(three.name, 'Abnormality of the cardiovascular system')
        self.assertEqual(three.category, hp.model.SynonymCategory.EXACT)
        self.assertEqual(three.synonym_type, hp.model.SynonymType.LAYPERSON_TERM)
        self.assertIsNone(three.xrefs)

        self.assertEqual(term.xrefs, [TermId.from_curie(curie) for curie in ('UMLS:C0243050', 'UMLS:C0007222',
                                                                             'MSH:D018376', 'SNOMEDCT_US:49601007',
                                                                             'MSH:D002318')])

    def test_synonym_properties(self):
        term = TestTerms.ONTOLOGY.get_term('HP:0001627')
        synonym = term.synonyms[7]
        self.assertEqual(synonym.name, 'Abnormally shaped heart')
        self.assertEqual(synonym.category, hp.model.SynonymCategory.EXACT)
        self.assertEqual(synonym.synonym_type, hp.model.SynonymType.LAYPERSON_TERM)
        self.assertEqual(synonym.xrefs, [TermId.from_curie('ORCID:0000-0001-5208-3432')])

