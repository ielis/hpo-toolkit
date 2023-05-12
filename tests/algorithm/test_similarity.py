import os
import unittest

from pkg_resources import resource_filename

from hpotk.algorithm.similarity import calculate_ic_for_annotated_items, precalculate_ic_mica_for_hpo_concept_pairs

from hpotk.model import TermId
from hpotk.annotations import HpoDiseases
from hpotk.annotations.load.hpoa import SimpleHpoaDiseaseLoader
from hpotk.ontology import MinimalOntology
from hpotk.ontology.load.obographs import load_minimal_ontology

TOY_HPO = resource_filename(__name__, os.path.join('../data', 'hp.small.json'))
TOY_HPOA = resource_filename(__name__, os.path.join('../data', 'phenotype.real-shortlist.hpoa'))


class TestResnik(unittest.TestCase):
    HPO: MinimalOntology
    DISEASES: HpoDiseases

    @classmethod
    def setUpClass(cls) -> None:
        cls.HPO: MinimalOntology = load_minimal_ontology(TOY_HPO)
        hpoa_loader = SimpleHpoaDiseaseLoader(cls.HPO)
        cls.DISEASES: HpoDiseases = hpoa_loader.load(TOY_HPOA)

    def test_calculate_ic_for_hpo_diseases(self):
        mica = calculate_ic_for_annotated_items(self.DISEASES, self.HPO)

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
            self.assertAlmostEqual(mica[term_id], ic)

        self.assertEqual(len(mica), 282)

    @unittest.skip
    def test_precalculate_mica_for_hpo_concept_pairs(self):
        # Takes ~15 seconds, and it isn't run regularly.
        term_id2ic = calculate_ic_for_annotated_items(self.DISEASES, self.HPO)

        sim_container = precalculate_ic_mica_for_hpo_concept_pairs(term_id2ic, self.HPO)

        self.assertAlmostEqual(sim_container.get_similarity('HP:0000118', 'HP:0000118'), 0.)  # Phenotypic abnormality

        # Arachnodactyly with Phenotypic abnormality
        self.assertAlmostEqual(sim_container.get_similarity('HP:0001166', 'HP:0000118'), 0.)
        # Arachnodactyly (self-similarity)
        self.assertAlmostEqual(sim_container.get_similarity('HP:0001166', 'HP:0001166'), 4.406719247264253)
        # Arachnodactyly with Abnormality of limbs
        self.assertAlmostEqual(sim_container.get_similarity('HP:0001166', 'HP:0040064'), 1.921812597476252)
        self.assertAlmostEqual(sim_container.get_similarity('HP:0040064', 'HP:0001166'), 1.921812597476252)

        # Total number of items
        self.assertEqual(len(sim_container), 50_928)
