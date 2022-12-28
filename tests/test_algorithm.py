import os
import unittest

import ddt
from pkg_resources import resource_filename

import hpotk as hp
from hpotk.model import TermId
from hpotk.ontology import MinimalOntology
from hpotk.ontology.load.obographs import load_minimal_ontology

TOY_HPO = resource_filename(__name__, os.path.join('data', 'hp.toy.json'))

hp.util.setup_logging()

HPO: MinimalOntology = load_minimal_ontology(TOY_HPO)


@ddt.ddt
class TestTraversal(unittest.TestCase):

    @ddt.data(
        ("HP:0001166", False, {"HP:0001238", "HP:0100807"}),
        ("HP:0001166", True, {"HP:0001166", "HP:0001238", "HP:0100807"})
    )
    @ddt.unpack
    def test_get_parents(self, source: str, include_source, expected):
        parents = hp.algorithm.get_parents(HPO, source, include_source)
        self.assertIsInstance(parents, frozenset)
        self.assertSetEqual(parents, {TermId.from_curie(val) for val in expected})

    @ddt.data(
        ("HP:0001166", False, {
            "HP:0001238", "HP:0100807", "HP:0011842", "HP:0033127", "HP:0002813", "HP:0040068",
            "HP:0002817", "HP:0011844", "HP:0011297", "HP:0000001", "HP:0001155", "HP:0040064",
            "HP:0000924", "HP:0000118", "HP:0001167"
        }),
        ("HP:0001166", True, {
            "HP:0001166", "HP:0001238", "HP:0100807", "HP:0011842", "HP:0033127", "HP:0002813", "HP:0040068",
            "HP:0002817", "HP:0011844", "HP:0011297", "HP:0000001", "HP:0001155", "HP:0040064", "HP:0000924",
            "HP:0000118", "HP:0001167"
        })
    )
    @ddt.unpack
    def test_get_ancestors(self, source: str, include_source, expected):
        ancestors = hp.algorithm.get_ancestors(HPO, source, include_source)
        self.assertIsInstance(ancestors, frozenset)
        self.assertSetEqual(ancestors, {TermId.from_curie(val) for val in expected})

    @ddt.data(
        ("HP:0001167", False, {"HP:0001238", "HP:0100807"}),
        ("HP:0001167", True, {"HP:0001167", "HP:0001238", "HP:0100807"})
    )
    @ddt.unpack
    def test_get_children(self, source: str, include_source, expected):
        children = hp.algorithm.get_children(HPO, source, include_source)
        self.assertIsInstance(children, frozenset)
        self.assertSetEqual(children, {TermId.from_curie(val) for val in expected})

    @ddt.data(
        ("HP:0001167", False, {"HP:0001166", "HP:0001238", "HP:0100807"}),
        ("HP:0001167", True, {"HP:0001167", "HP:0001166", "HP:0001238", "HP:0100807"})
    )
    @ddt.unpack
    def test_get_descendents(self, source: str, include_source, expected):
        descendents = hp.algorithm.get_descendents(HPO, source, include_source)
        self.assertIsInstance(descendents, frozenset)
        self.assertSetEqual(descendents, {TermId.from_curie(val) for val in expected})

    def test_we_get_correct_number_of_descendents(self):
        all_term_id = "HP:0000001"
        self.assertEqual(len(HPO) - 1, len(hp.algorithm.get_descendents(HPO, all_term_id)))
        self.assertEqual(len(HPO), len(hp.algorithm.get_descendents(HPO, all_term_id, include_source=True)))
