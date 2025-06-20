import typing

import pytest

import hpotk
from hpotk.annotations import HpoDiseases, HpoDiseaseAnnotation
from hpotk.annotations.load.hpoa import SimpleHpoaDiseaseLoader


class TestHpoaLoader:

    def test_load_hpo_annotations(
        self,
        hpoa_disease_loader: SimpleHpoaDiseaseLoader,
        fpath_toy_hpoa: str,
    ):
        diseases = hpoa_disease_loader.load(fpath_toy_hpoa)
        assert isinstance(diseases, HpoDiseases)

        assert 2 == len(diseases)
        assert {'ORPHA:123456', 'OMIM:987654'} == set(map(lambda di: di.value, diseases.item_ids()))
        assert diseases.version == '2021-08-02'

    def test_load_older_hpo_annotations(
        self,
        hpoa_disease_loader: SimpleHpoaDiseaseLoader,
        fpath_toy_hpoa_older: str,
    ):
        diseases = hpoa_disease_loader.load(fpath_toy_hpoa_older)
        assert isinstance(diseases, HpoDiseases)

        assert 2 == len(diseases)
        assert {'ORPHA:123456', 'OMIM:987654'} == set(map(lambda di: di.value, diseases.item_ids()))


class TestHpoaDiseaseProperties:

    @pytest.fixture(scope="class")
    def toy_hpo_diseases(
        self,
        hpoa_disease_loader: SimpleHpoaDiseaseLoader,
        fpath_toy_hpoa: str,
    ) -> HpoDiseases:
        return hpoa_disease_loader.load(fpath_toy_hpoa)

    def test_hpoa_disease_properties(
        self,
        toy_hpo_diseases: HpoDiseases,
        hpoa_disease_loader: SimpleHpoaDiseaseLoader,
    ):
        omim = toy_hpo_diseases['OMIM:987654']
        assert omim is not None
        assert 'Made-up OMIM disease, autosomal recessive', omim.name
        assert 2, len(omim.annotations)
        assert len(omim.onsets) == 1
        assert hpotk.TermId.from_curie("HP:0003577") in omim.onsets

        omim_annotations: typing.Sequence[HpoDiseaseAnnotation] = sorted(omim.annotations, key=lambda a: a.identifier.value) # type: ignore
        
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
        assert second.denominator == hpoa_disease_loader.cohort_size
        assert len(second.references) == 1
