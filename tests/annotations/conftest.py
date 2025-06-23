import pytest

import hpotk
from hpotk.annotations.load.hpoa import SimpleHpoaDiseaseLoader


@pytest.fixture(scope="package")
def hpoa_disease_loader(toy_hpo: hpotk.MinimalOntology) -> SimpleHpoaDiseaseLoader:
    return SimpleHpoaDiseaseLoader(toy_hpo)
