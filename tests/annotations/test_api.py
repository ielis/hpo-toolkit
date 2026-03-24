import pytest

import hpotk
from hpotk.annotations import HpoDiseases, HpoDisease
from hpotk.annotations.load import HpoDiseaseLoader


class TestHpoDiseases:
    @pytest.fixture(scope="class")
    def hpo_diseases(
        self,
        hpoa_disease_loader: HpoDiseaseLoader,
        fpath_toy_hpoa: str,
    ) -> HpoDiseases:
        return hpoa_disease_loader.load(fpath_toy_hpoa)

    def test_properties(
        self,
        hpo_diseases: HpoDiseases,
    ):
        items = tuple(hpo_diseases)

        # We can iterate over diseases ...
        assert all(isinstance(item, HpoDisease) for item in items)
        assert sorted(item.identifier.value for item in items) == [
            "OMIM:987654",
            "ORPHA:123456",
        ]

        # ... and we can test the number of diseases.
        assert len(items) == 2

    def test_getitem(
        self,
        hpo_diseases: HpoDiseases,
    ):
        curie = "OMIM:987654"
        # We can query by a CURIE `str` ...
        disease = hpo_diseases[curie]
        assert disease is not None
        assert disease.identifier.value == curie

        # ... or by a TermId.
        disease = hpo_diseases[hpotk.TermId.from_curie(curie)]
        assert disease is not None
        assert disease.identifier.value == curie

        # Unknown/absent disease
        assert hpo_diseases["OMIM:123456"] is None

    def test_version(
        self,
        hpo_diseases: HpoDiseases,
    ):
        assert hpo_diseases.version == "2021-08-02"
