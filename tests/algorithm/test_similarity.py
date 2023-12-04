import os

import pytest
from pkg_resources import resource_filename

import hpotk
from hpotk.algorithm.similarity import calculate_ic_for_annotated_items, precalculate_ic_mica_for_hpo_concept_pairs

from hpotk.model import TermId
from hpotk.annotations.load.hpoa import SimpleHpoaDiseaseLoader
from hpotk.ontology.load.obographs import load_minimal_ontology

TOY_HPO = resource_filename(__name__, os.path.join('../data', 'hp.small.json'))
# TOY_HPO = '/home/ielis/data/ontologies/hpo/2023-04-05/hp.2023-04-05.json'
TOY_HPOA = resource_filename(__name__, os.path.join('../data', 'phenotype.real-shortlist.hpoa'))
# TOY_HPOA = '/home/ielis/data/hpoa/phenotype.2023-04-05.hpoa'


class TestResnik:

    @pytest.fixture(scope='class')
    def toy_hpo(self) -> hpotk.MinimalOntology:
        return load_minimal_ontology(TOY_HPO)

    @pytest.fixture(scope='class')
    def toy_hpoa(self, toy_hpo: hpotk.MinimalOntology) -> hpotk.annotations.HpoDiseases:
        hpoa_loader = SimpleHpoaDiseaseLoader(toy_hpo)
        return hpoa_loader.load(TOY_HPOA)

    @pytest.mark.skip('Skipped for now')
    def test_precalculate_and_store(self, toy_hpo: hpotk.MinimalOntology,
                                    toy_hpoa: hpotk.annotations.HpoDiseases):
        mica = calculate_ic_for_annotated_items(toy_hpoa, toy_hpo)
        mica.to_csv('ic.csv.gz')

    def test_calculate_ic_for_hpo_diseases(self, toy_hpo: hpotk.MinimalOntology,
                                           toy_hpoa: hpotk.annotations.HpoDiseases):
        container = calculate_ic_for_annotated_items(toy_hpoa, toy_hpo)

        expected = {
            # All the way down to Arachnodactyly
            'HP:0000001': 0.,  # All
            'HP:0000118': 0.,  # Phenotypic abnormality
            'HP:0040064': 1.921812597476252,  # Abnormality of limbs
            'HP:0002817': 3.713572066704308,  # Abnormality of the upper limb
            'HP:0001155': 4.406719247264253,  # Abnormality of the hand
            'HP:0001167': 4.406719247264253,  # Abnormal finger morphology
            'HP:0100807': 4.406719247264253,  # Long fingers
            'HP:0001166': 4.406719247264253,  # Arachnodactyly

            # Check some other terms
            'HP:0012373': 2.1041341542702074,  # Abnormal eye physiology
            'HP:0033127': 1.1108823812599240,  # Abnormality of the musculoskeletal system
            'HP:0000924': 1.3621968095408301,  # Abnormality of the skeletal system
        }

        for curie, ic in expected.items():
            term_id = TermId.from_curie(curie)
            assert container[term_id] == pytest.approx(ic)

        assert 282 == len(container)

        # HP:0000160 Narrow mouth does not annotate any items from self.DISEASES.
        # Hence, it is not in the `container`
        assert TermId.from_curie('HP:0000160') not in container
        # With the current `self.DISEASES`, the items are not annotated with all ontology terms.
        assert len(toy_hpo) != len(container)

    def test_calculate_ic_for_hpo_diseases__use_pseudocount(self, toy_hpo: hpotk.MinimalOntology,
                                                            toy_hpoa: hpotk.annotations.HpoDiseases):
        container = calculate_ic_for_annotated_items(toy_hpoa, toy_hpo, use_pseudocount=True)

        assert len(toy_hpo) == len(container)

        # HP:0000160 Narrow mouth does not annotate any items from self.DISEASES.
        # Yet, as a result of `use_pseudocount`, we have an IC value.
        assert 4.406719247264253 == pytest.approx(container[TermId.from_curie('HP:0000160')])
        # Similarly, we have IC for ALL ontology terms
        assert len(toy_hpo) == len(container)

    def test_calculate_ic_for_hpo_diseases__submodule(self, toy_hpo: hpotk.MinimalOntology,
                                                      toy_hpoa: hpotk.annotations.HpoDiseases):
        module_root = TermId.from_curie('HP:0012372')  # Abnormal eye morphology
        container = calculate_ic_for_annotated_items(toy_hpoa, toy_hpo, module_root=module_root)

        # The IC of the module root is 0.
        assert 0. == pytest.approx(container[module_root])

        # All container elements are descendants (incl) of the module root.
        descendants = set(toy_hpo.graph.get_descendants(module_root, include_source=True))
        assert all(term_id in descendants for term_id in container.keys())

        # We do not have IC for terms that are not descendants of the module root
        all_term_ids = set(map(lambda t: t.identifier, toy_hpo.terms))
        others = all_term_ids.difference(descendants)
        assert not any(other in container for other in others)

    def test_calculate_ic_for_hpo_diseases__submodule_and_use_pseudocount(self, toy_hpo: hpotk.MinimalOntology,
                                                                          toy_hpoa: hpotk.annotations.HpoDiseases):
        module_root = TermId.from_curie('HP:0012372')  # Abnormal eye morphology
        container = calculate_ic_for_annotated_items(toy_hpoa, toy_hpo,
                                                     module_root=module_root, use_pseudocount=True)

        # The IC of the module root is 0.
        assert 0. == pytest.approx(container[module_root])

        # All container elements are descendants (incl) of the module root.
        descendants = set(toy_hpo.graph.get_descendants(module_root, include_source=True))
        assert all(term_id in descendants for term_id in container.keys())

        # We have IC for all descendants
        assert all(term_id in container for term_id in descendants)

        # We do not have IC for terms that are not descendants of the module root
        all_term_ids = set(map(lambda t: t.identifier, toy_hpo.terms))
        others = all_term_ids.difference(descendants)
        assert not any(other in container for other in others)

    @pytest.mark.skip('Skipped for now')
    def test_precalculate_mica_for_hpo_concept_pairs(self, toy_hpo: hpotk.MinimalOntology,
                                                     toy_hpoa: hpotk.annotations.HpoDiseases):
        # Takes ~15 seconds, and it isn't run regularly.
        term_id2ic = calculate_ic_for_annotated_items(toy_hpoa, toy_hpo)

        sim_container = precalculate_ic_mica_for_hpo_concept_pairs(term_id2ic, toy_hpo)

        assert sim_container.get_similarity('HP:0000118', 'HP:0000118'), pytest.approx(0.)  # Phenotypic abnormality

        # Arachnodactyly with Phenotypic abnormality
        assert sim_container.get_similarity('HP:0001166', 'HP:0000118'), pytest.approx(0.)
        # Arachnodactyly (self-similarity)
        assert sim_container.get_similarity('HP:0001166', 'HP:0001166') == pytest.approx(4.406719247264253)
        # Arachnodactyly with Abnormality of limbs
        assert sim_container.get_similarity('HP:0001166', 'HP:0040064') == pytest.approx(1.921812597476252)
        assert sim_container.get_similarity('HP:0040064', 'HP:0001166') == pytest.approx(1.921812597476252)

        # Total number of items
        assert len(sim_container) == 50_928
