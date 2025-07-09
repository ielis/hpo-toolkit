import typing

import pytest

import hpotk
from hpotk.annotations import HpoDiseases, HpoDisease, HpoDiseaseAnnotation
from hpotk.annotations.load.hpoa import SimpleHpoaDiseaseLoader
from hpotk.constants.hpo.inheritance import (
    AUTOSOMAL_DOMINANT_INHERITANCE,
    AUTOSOMAL_RECESSIVE_INHERITANCE,
)


class TestHpoaLoader:
    def test_load_hpo_annotations(
        self,
        hpoa_disease_loader: SimpleHpoaDiseaseLoader,
        fpath_toy_hpoa: str,
    ):
        diseases = hpoa_disease_loader.load(fpath_toy_hpoa)
        assert isinstance(diseases, HpoDiseases)

        assert 2 == len(diseases)
        assert {"ORPHA:123456", "OMIM:987654"} == set(map(lambda di: di.value, diseases.item_ids()))
        assert diseases.version == "2021-08-02"

    def test_load_older_hpo_annotations(
        self,
        hpoa_disease_loader: SimpleHpoaDiseaseLoader,
        fpath_toy_hpoa_older: str,
    ):
        diseases = hpoa_disease_loader.load(fpath_toy_hpoa_older)
        assert isinstance(diseases, HpoDiseases)

        assert 2 == len(diseases)
        assert {"ORPHA:123456", "OMIM:987654"} == set(map(lambda di: di.value, diseases.item_ids()))

    def test_load_real_shortlist(
        self,
        hpoa_disease_loader: SimpleHpoaDiseaseLoader,
        fpath_real_shortlist_hpoa: str,
    ):
        """
        Test parsing of onsets, frequencies, and modes of inheritance.
        """
        diseases = hpoa_disease_loader.load(fpath_real_shortlist_hpoa)

        hyperekplexia2 = diseases["OMIM:154700"]
        assert hyperekplexia2 is not None
        TestHpoaLoader.check_marfan(hyperekplexia2)

        hyperekplexia2 = diseases["OMIM:614619"]
        assert hyperekplexia2 is not None
        TestHpoaLoader.check_hyperekplexia2(hyperekplexia2)

    @staticmethod
    def check_marfan(disease: HpoDisease):
        assert disease.identifier.value == "OMIM:154700"
        assert disease.name == "Marfan syndrome"

        assert len(disease.modes_of_inheritance) == 1
        assert AUTOSOMAL_DOMINANT_INHERITANCE in disease.modes_of_inheritance

        assert len(disease.onsets) == 0

        assert len(disease.annotations) == 68

        ann = disease.annotation_by_id("HP:0032934")  # Spontaneous cerebrospinal fluid leak
        assert ann is not None
        assert ann.identifier.value == "HP:0032934"
        assert (ann.numerator, ann.denominator) == (1, 50)

        assert len(ann.onsets) == 2
        assert all(hpotk.TermId.from_curie(curie) in ann.onsets for curie in ("HP:0011462", "HP:0003581"))

        assert ann.onset_counts("HP:0003674") is None  # Onset
        assert ann.onset_counts("HP:0003581") == (1, 50)  # Adult onset
        assert ann.onset_counts("HP:0011462") == (1, 50)  # Young adult onset

    @staticmethod
    def check_hyperekplexia2(disease: HpoDisease):
        assert disease.identifier.value == "OMIM:614619"
        assert disease.name == "Hyperekplexia 2"

        assert len(disease.modes_of_inheritance) == 1
        assert AUTOSOMAL_RECESSIVE_INHERITANCE in disease.modes_of_inheritance

        assert len(disease.onsets) == 2
        assert all(hpotk.TermId.from_curie(curie) in disease.onsets for curie in ("HP:0003623", "HP:0003577"))


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
        omim = toy_hpo_diseases["OMIM:987654"]
        assert omim is not None
        assert "Made-up OMIM disease, autosomal recessive", omim.name
        assert 2, len(omim.annotations)
        assert len(omim.onsets) == 1
        assert hpotk.TermId.from_curie("HP:0003577") in omim.onsets

        omim_annotations: typing.Sequence[HpoDiseaseAnnotation] = sorted(
            omim.annotations, key=lambda a: a.identifier.value
        )  # type: ignore

        first = omim_annotations[0]
        assert first.identifier.value == "HP:0001167"
        assert first.is_present
        assert first.numerator == 5
        assert first.denominator == 13
        assert len(first.references) == 2
        assert {m.value for m in first.modifiers} == {"HP:0012832", "HP:0012828"}

        second = omim_annotations[1]
        assert second.identifier.value == "HP:0001238"
        assert second.is_excluded
        assert second.numerator == 0
        assert second.denominator == hpoa_disease_loader.cohort_size
        assert len(second.references) == 1
