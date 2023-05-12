import os
import typing
import unittest

import hpotk
from pkg_resources import resource_filename

TOY_HPO = resource_filename(__name__, os.path.join('../../data', 'hp.toy.json'))
TOY_HPOA_OLDER = resource_filename(__name__, os.path.join('../../data', 'phenotype.fake.older.hpoa'))
TOY_HPOA = resource_filename(__name__, os.path.join('../../data', 'phenotype.fake.novel.hpoa'))


class TestHpoaLoaderBase(unittest.TestCase):
    HPO: hpotk.ontology.MinimalOntology

    @classmethod
    def setUpClass(cls) -> None:
        cls.HPO = hpotk.ontology.load.obographs.load_minimal_ontology(TOY_HPO)


class TestHpoaLoader(TestHpoaLoaderBase):

    @classmethod
    def setUpClass(cls) -> None:
        TestHpoaLoaderBase.setUpClass()

    def setUp(self) -> None:
        self.loader = hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader(TestHpoaLoaderBase.HPO)

    def test_load_hpo_annotations(self):
        diseases = self.loader.load(TOY_HPOA)
        self.assertIsInstance(diseases, hpotk.annotations.HpoDiseases)

        self.assertEqual(2, len(diseases))
        self.assertSetEqual({'ORPHA:123456', 'OMIM:987654'}, set(map(lambda di: di.value, diseases.item_ids())))
        self.assertEqual(diseases.version, '2021-08-02')

    def test_load_older_hpo_annotations(self):
        diseases = self.loader.load(TOY_HPOA_OLDER)
        self.assertIsInstance(diseases, hpotk.annotations.HpoDiseases)

        self.assertEqual(2, len(diseases))
        self.assertSetEqual({'ORPHA:123456', 'OMIM:987654'}, set(map(lambda di: di.value, diseases.item_ids())))


class TestHpoaDiseaseProperties(TestHpoaLoaderBase):
    LOADER: hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader
    HPO_DISEASES: hpotk.annotations.HpoDiseases

    @classmethod
    def setUpClass(cls) -> None:
        TestHpoaLoaderBase.setUpClass()
        cls.LOADER = hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader(TestHpoaLoaderBase.HPO)
        cls.HPO_DISEASES = cls.LOADER.load(TOY_HPOA)

    def test_hpoa_disease_properties(self):
        omim = TestHpoaDiseaseProperties.HPO_DISEASES['OMIM:987654']
        self.assertEqual('Made-up OMIM disease, autosomal recessive', omim.name)
        self.assertEqual(2, len(omim.annotations))

        omim_annotations: typing.List[hpotk.annotations.HpoDiseaseAnnotation] = list(
            sorted(omim.annotations, key=lambda a: a.identifier.value))
        first = omim_annotations[0]
        self.assertEqual(first.identifier.value, 'HP:0001167')
        self.assertEqual(first.is_present, True)
        self.assertEqual(first.ratio.numerator, 5)
        self.assertEqual(first.ratio.denominator, 13)
        self.assertEqual(len(first.references), 2)
        self.assertSetEqual({m.value for m in first.modifiers}, {'HP:0012832', 'HP:0012828'})

        second = omim_annotations[1]
        self.assertEqual(second.identifier.value, 'HP:0001238')
        self.assertEqual(second.is_absent, True)
        self.assertEqual(second.ratio.numerator, 0)
        self.assertEqual(second.ratio.denominator, TestHpoaDiseaseProperties.LOADER.cohort_size)
        self.assertEqual(len(second.references), 1)
