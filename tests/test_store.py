import os
from pathlib import Path

import pytest

import hpotk


@pytest.mark.skip('Needs an internet connection')
class TestGitHubOntologyStore:

    def test_load_minimal_hpo(
            self,
            tmp_path: Path,
    ):
        assert len(os.listdir(tmp_path)) == 0  # We start with the clean slate.

        store = hpotk.configure_ontology_store(store_dir=str(tmp_path))
        assert len(os.listdir(tmp_path)) == 0  # Creating the store does nothing.

        release = 'v2024-03-06'
        hpo = store.load_minimal_hpo(release=release)

        assert isinstance(hpo, hpotk.MinimalOntology)
        assert hpo.version == release[1:]

        fpath_expected = os.path.join(tmp_path, 'HP', f'hp.{release}.json')
        assert os.path.isfile(fpath_expected)

    def test_load_minimal_hpo__invalid_release(
            self,
            tmp_path: Path,
    ):
        store = hpotk.configure_ontology_store(store_dir=str(tmp_path))

        release = 'v3400-12-31'
        with pytest.raises(ValueError) as e:
            store.load_minimal_hpo(release=release)

        assert e.value.args[0] == f'Could not find {release} on GitHub'
