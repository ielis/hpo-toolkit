import os
import typing

import pytest

import hpotk
from pkg_resources import resource_filename

TOY_HPO = resource_filename(__name__, os.path.join('../../data', 'hp.toy.json'))
TOY_HPOA_OLDER = resource_filename(__name__, os.path.join('../../data', 'phenotype.fake.older.hpoa'))
TOY_HPOA = resource_filename(__name__, os.path.join('../../data', 'phenotype.fake.novel.hpoa'))


class TestHpoaLoaderBase:

    @pytest.fixture
    def toy_hpo(self) -> hpotk.MinimalOntology:
        return hpotk.load_minimal_ontology(TOY_HPO)

    @pytest.fixture
    def loader(self, toy_hpo: hpotk.MinimalOntology) -> hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader:
        return hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader(toy_hpo)


class TestHpoaLoader(TestHpoaLoaderBase):

    def test_load_hpo_annotations(self, loader: hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader):
        diseases = loader.load(TOY_HPOA)
        assert isinstance(diseases, hpotk.annotations.HpoDiseases)

        assert 2 == len(diseases)
        assert {'ORPHA:123456', 'OMIM:987654'} == set(map(lambda di: di.value, diseases.item_ids()))
        assert diseases.version == '2021-08-02'

    def test_load_older_hpo_annotations(self, loader: hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader):
        diseases = loader.load(TOY_HPOA_OLDER)
        assert isinstance(diseases, hpotk.annotations.HpoDiseases)

        assert 2 == len(diseases)
        assert {'ORPHA:123456', 'OMIM:987654'} == set(map(lambda di: di.value, diseases.item_ids()))


class TestHpoaDiseaseProperties(TestHpoaLoaderBase):

    @pytest.fixture
    def toy_hpo_diseases(self,
                         loader: hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader) -> hpotk.annotations.HpoDiseases:
        return loader.load(TOY_HPOA)

    def test_hpoa_disease_properties(self, toy_hpo_diseases: hpotk.annotations.HpoDiseases,
                                     loader: hpotk.annotations.load.hpoa.SimpleHpoaDiseaseLoader):
        omim = toy_hpo_diseases['OMIM:987654']
        assert 'Made-up OMIM disease, autosomal recessive', omim.name
        assert 2, len(omim.annotations)

        omim_annotations: typing.List[hpotk.annotations.HpoDiseaseAnnotation] = list(
            sorted(omim.annotations, key=lambda a: a.identifier.value))
        first = omim_annotations[0]
        assert first.identifier.value == 'HP:0001167'
        assert first.is_present
        assert first.numerator == 5
        assert first.denominator == 13
        assert len(first.references) == 2
        assert {m.value for m in first.modifiers} == {'HP:0012832', 'HP:0012828'}

        second = omim_annotations[1]
        assert second.identifier.value == 'HP:0001238'
        assert second.is_excluded
        assert second.numerator == 0
        assert second.denominator == loader.cohort_size
        assert len(second.references) == 1
