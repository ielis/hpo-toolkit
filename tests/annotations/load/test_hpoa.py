import os
import typing
import unittest

import hpotk
from pkg_resources import resource_filename

TOY_HPO = resource_filename(__name__, os.path.join('../../data', 'hp.toy.json'))
TOY_HPOA = resource_filename(__name__, os.path.join('../../data', 'phenotype.fake.hpoa'))


class TestHpoaLoader(unittest.TestCase):

    HPO: hpotk.ontology.MinimalOntology

    @classmethod
    def setUpClass(cls) -> None:
        cls.HPO = hpotk.ontology.load.obographs.load_minimal_ontology(TOY_HPO)

    def setUp(self) -> None:
        self.loader = hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader(self.HPO)

    def test_toy_phenotypic_features(self):
        diseases = self.loader.load(TOY_HPOA)
        self.assertIsInstance(diseases, hpotk.annotations.HpoDiseases)

        self.assertEqual(2, len(diseases))
        self.assertSetEqual({'ORPHA:123456', 'OMIM:987654'}, set(map(lambda d: d.value, diseases.disease_ids)))

        omim = diseases['OMIM:987654']
        self.assertEqual('Made-up OMIM disease, autosomal recessive', omim.name)
        self.assertEqual(2, len(omim.annotations))

        omim_annotations: typing.List[hpotk.annotations.HpoDiseaseAnnotation] = list(sorted(omim.annotations, key=lambda a: a.identifier.value))
        first = omim_annotations[0]
        self.assertEqual(first.identifier.value, 'HP:0001167')
        self.assertEqual(first.is_present(), True)
        self.assertEqual(first.ratio.numerator, 5)
        self.assertEqual(first.ratio.denominator, 13)
        self.assertEqual(len(first.references), 2)
        self.assertSetEqual({m.value for m in first.modifiers}, {'HP:0012832', 'HP:0012828'})

        second = omim_annotations[1]
        self.assertEqual(second.identifier.value, 'HP:0001238')
        self.assertEqual(second.is_absent(), True)
        self.assertEqual(second.ratio.numerator, 0)
        self.assertEqual(second.ratio.denominator, self.loader.cohort_size)
        self.assertEqual(len(second.references), 1)

    def test_disease_data_has_version(self):
        diseases: hpotk.annotations.HpoDiseases = self.loader.load(TOY_HPOA)
        self.assertEqual(diseases.version, '2021-08-02')

    # @unittest.skip
    def test_real(self):
        hpo = hpotk.ontology.load.obographs.load_minimal_ontology('/home/ielis/data/ontologies/hpo/2022-10-05/hp.json')
        loader = hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader(hpo)
        diseases = loader.load('/home/ielis/data/hpoa/phenotype.hpoa')
        self.assertIsInstance(diseases, hpotk.annotations.HpoDiseases)
