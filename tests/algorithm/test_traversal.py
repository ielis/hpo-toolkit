import os

import pytest
from pkg_resources import resource_filename

import hpotk
from hpotk.model import TermId
from hpotk.ontology.load.obographs import load_minimal_ontology

TOY_HPO = resource_filename(__name__, os.path.join('../data', 'hp.toy.json'))


class TestTraversal:

    @pytest.fixture(scope='class')
    def toy_hpo(self) -> hpotk.MinimalOntology:
        return load_minimal_ontology(TOY_HPO)

    @pytest.mark.parametrize('source, include_source, expected',
                             [
                                 ("HP:0001166", False, {"HP:0001238", "HP:0100807"}),
                                 ("HP:0001166", True, {"HP:0001166", "HP:0001238", "HP:0100807"})
                             ])
    def test_get_parents(self, source: str, include_source, expected, toy_hpo: hpotk.MinimalOntology):
        parents = set(toy_hpo.graph.get_parents(source, include_source))
        assert parents == {TermId.from_curie(val) for val in expected}

    @pytest.mark.parametrize('source, include_source, expected',
                             [("HP:0001166", False,
                               {
                                   "HP:0001238", "HP:0100807", "HP:0011842", "HP:0033127", "HP:0002813", "HP:0040068",
                                   "HP:0002817", "HP:0011844", "HP:0011297", "HP:0000001", "HP:0001155", "HP:0040064",
                                   "HP:0000924", "HP:0000118", "HP:0001167"
                               }),
                              ("HP:0001166", True,
                               {
                                   "HP:0001166", "HP:0001238", "HP:0100807", "HP:0011842", "HP:0033127", "HP:0002813",
                                   "HP:0040068",
                                   "HP:0002817", "HP:0011844", "HP:0011297", "HP:0000001", "HP:0001155", "HP:0040064",
                                   "HP:0000924",
                                   "HP:0000118", "HP:0001167"
                               })])
    def test_get_ancestors(self, source: str, include_source, expected, toy_hpo: hpotk.MinimalOntology):
        ancestors = set(toy_hpo.graph.get_ancestors(source, include_source))
        assert ancestors == {TermId.from_curie(val) for val in expected}

    @pytest.mark.parametrize('source, include_source, expected',
                             [
                                 ("HP:0001167", False, {"HP:0001238", "HP:0100807"}),
                                 ("HP:0001167", True, {"HP:0001167", "HP:0001238", "HP:0100807"})
                             ])
    def test_get_children(self, source: str, include_source, expected, toy_hpo: hpotk.MinimalOntology):
        children = set(toy_hpo.graph.get_children(source, include_source))
        assert children == {TermId.from_curie(val) for val in expected}

    @pytest.mark.parametrize('source, include_source, expected',
                             [
                                 ("HP:0001167", False, {"HP:0001166", "HP:0001238", "HP:0100807"}),
                                 ("HP:0001167", True, {"HP:0001167", "HP:0001166", "HP:0001238", "HP:0100807"})
                             ])
    def test_get_descendants(self, source: str, include_source, expected, toy_hpo: hpotk.MinimalOntology):
        descendants = set(toy_hpo.graph.get_descendants(source, include_source))
        assert descendants == {TermId.from_curie(val) for val in expected}

    def test_we_get_correct_number_of_descendants(self, toy_hpo: hpotk.MinimalOntology):
        all_term_id = "HP:0000001"
        assert len(toy_hpo) - 1 == len(list(toy_hpo.graph.get_descendants(all_term_id)))
        assert len(toy_hpo) == len(list(toy_hpo.graph.get_descendants(all_term_id, include_source=True)))
