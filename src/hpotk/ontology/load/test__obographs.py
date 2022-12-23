import os
import unittest

from pkg_resources import resource_filename

import hpotk as hp
from hpotk.ontology.load.obographs import load_ontology, load_minimal_ontology

TOY_HPO = resource_filename(__name__, os.path.join('test_data', 'hp.toy.json'))


class TestObographs(unittest.TestCase):

    def test_load_minimal_ontology(self):
        o: hp.ontology.MinimalOntology = load_minimal_ontology(TOY_HPO)
        self.assertIsNotNone(o, "Ontology must not be None")
        self.assertIsInstance(o, hp.ontology.MinimalOntology)
        self.assertEqual(82, len(o), "There must be 82 terms in the ontology")
        self.assertEqual(150, len(list(o.term_ids)), "There must be 150 term IDs in the ontology")
        self.assertEqual(150, len(set(o.term_ids)), "There must be 150 unique term IDs in the ontology")
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
        self.assertEqual(82, len(o), "There must be 82 terms in the ontology")
        self.assertEqual(150, len(list(o.term_ids)), "There must be 150 term IDs in the ontology")
        self.assertEqual(150, len(set(o.term_ids)), "There must be 150 unique term IDs in the ontology")
        self.assertTrue(all([term_id in o for term_id in o.term_ids]), "The ontology must contain all term IDs")
        self.assertTrue(all([o.get_term(k) is not None for k in o.term_ids]),
                        "The `get_term` must get primary term for any term ID from ontology")
        self.assertTrue(all([o.get_term(k).identifier == k or k in o.get_term(k).alt_term_ids for k in o.term_ids]),
                        "Each term ID must be either primary or alternative ID")
