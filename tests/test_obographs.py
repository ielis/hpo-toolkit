import os
import unittest

from pkg_resources import resource_filename

import hpotk as hp
from hpotk.model import TermId
from hpotk.ontology.load.obographs import *

TOY_HPO = resource_filename(__name__, os.path.join('data', 'hp.toy.json'))

hp.util.setup_logging()


class TestObographs(unittest.TestCase):

    def test_load_minimal_ontology(self):
        o: hp.ontology.MinimalOntology = load_minimal_ontology(TOY_HPO)
        self.assertIsNotNone(o, "Ontology must not be None")
        self.assertIsInstance(o, hp.ontology.MinimalOntology)
        self.assertEqual(o.version, '2022-10-05')
        self.assertEqual(393, len(o), "There must be 393 terms in the ontology")
        self.assertEqual(557, len(list(o.term_ids)), "There must be 557 term IDs in the ontology")
        self.assertEqual(557, len(set(o.term_ids)), "There must be 557 unique term IDs in the ontology")
        self.assertTrue(all([term_id in o for term_id in o.term_ids]), "The ontology must contain all term IDs")
        self.assertTrue(all([o.get_term(k) is not None for k in o.term_ids]),
                        "The `get_term` must get primary term for any term ID from ontology")
        self.assertTrue(all([o.get_term(k.value) is not None for k in o.term_ids]),
                        "The `get_term` must get primary term for any term ID value from ontology")
        self.assertTrue(all([o.get_term(k).identifier == k or k in o.get_term(k).alt_term_ids for k in o.term_ids]),
                        "Each term ID must be either primary or alternative ID")

    def test_load_ontology(self):
        o: hp.ontology.Ontology = load_ontology(TOY_HPO)
        self.assertIsNotNone(o, "Ontology must not be None")
        self.assertIsInstance(o, hp.ontology.Ontology)
        self.assertEqual(o.version, '2022-10-05')
        self.assertEqual(393, len(o), "There must be 393 terms in the ontology")
        self.assertEqual(557, len(list(o.term_ids)), "There must be 557 term IDs in the ontology")
        self.assertEqual(557, len(set(o.term_ids)), "There must be 557 unique term IDs in the ontology")
        self.assertTrue(all([term_id in o for term_id in o.term_ids]), "The ontology must contain all term IDs")
        self.assertTrue(all([o.get_term(k) is not None for k in o.term_ids]),
                        "The `get_term` must get primary term for any term ID from ontology")
        self.assertTrue(all([o.get_term(k).identifier == k or k in o.get_term(k).alt_term_ids for k in o.term_ids]),
                        "Each term ID must be either primary or alternative ID")

    def test_load_minimal_ontology_backed_by_csr(self):
        term_factory = hp.ontology.load.obographs.MinimalTermFactory()
        graph_factory = hp.graph.CsrGraphFactory()
        o: hp.ontology.MinimalOntology = load_minimal_ontology(TOY_HPO, term_factory=term_factory, graph_factory=graph_factory)
        self.assertIsNotNone(o, "Ontology must not be None")

        arachnodactyly = TermId.from_curie("HP:0001166")
        assert all([val.value in {"HP:0001238", "HP:0100807"} for val in (o.graph.get_parents(arachnodactyly))])
        assert len(list(o.graph.get_children(arachnodactyly))) == 0

    @unittest.skip
    def test_print_stats(self):
        import json
        with open(TOY_HPO) as fh:
            graphs = json.load(fh)

        graph = graphs['graphs'][0]
        all_nodes = graph['nodes']
        all_edges = graph['edges']
        print(f'All nodes: {len(all_nodes)}, all edges: {len(all_edges)}')
        current_nodes = self._get_current_nodes(all_nodes)
        print(f'Current nodes: {len(current_nodes)}')
        # Getting the number of all term IDs is too complicated to be implemented here at this moment.
        # The functionality should be implemented later if necessary.

    @staticmethod
    def _get_current_nodes(nodes):
        result = []
        for node in nodes:
            if 'meta' in node:
                meta = node['meta']
                if 'deprecated' in meta:
                    deprecated = meta['deprecated']
                    if not deprecated:
                        result.append(node)
                else:
                    result.append(node)
        return result


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
        self.assertEqual(one.synonym_category, hp.model.SynonymCategory.RELATED)
        self.assertEqual(one.synonym_type, hp.model.SynonymType.LAYPERSON_TERM)
        self.assertIsNone(one.xrefs)

        two = synonyms[1]
        self.assertEqual(two.name, 'Cardiovascular abnormality')
        self.assertEqual(two.synonym_category, hp.model.SynonymCategory.EXACT)
        self.assertEqual(two.synonym_type, hp.model.SynonymType.LAYPERSON_TERM)
        self.assertIsNone(two.xrefs)

        three = synonyms[2]
        self.assertEqual(three.name, 'Abnormality of the cardiovascular system')
        self.assertEqual(three.synonym_category, hp.model.SynonymCategory.EXACT)
        self.assertEqual(three.synonym_type, hp.model.SynonymType.LAYPERSON_TERM)
        self.assertIsNone(three.xrefs)

        self.assertEqual(term.xrefs, [TermId.from_curie(curie) for curie in ('UMLS:C0243050', 'UMLS:C0007222',
                                                                             'MSH:D018376', 'SNOMEDCT_US:49601007',
                                                                             'MSH:D002318')])

    def test_synonym_properties(self):
        term = TestTerms.ONTOLOGY.get_term('HP:0001627')
        synonym = term.synonyms[7]
        self.assertEqual(synonym.name, 'Abnormally shaped heart')
        self.assertEqual(synonym.synonym_category, hp.model.SynonymCategory.EXACT)
        self.assertEqual(synonym.synonym_type, hp.model.SynonymType.LAYPERSON_TERM)
        self.assertEqual(synonym.xrefs, [TermId.from_curie('ORCID:0000-0001-5208-3432')])

