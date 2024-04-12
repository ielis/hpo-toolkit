import io
import os
import typing
from pathlib import Path

import pytest

import hpotk


class MockRemoteOntologyService(hpotk.store.RemoteOntologyService):

    def __init__(
            self,
            release: str,
            payload: bytes,
    ):
        self._release = release
        self._payload = payload

    def fetch_ontology(
            self,
            ontology_type: hpotk.OntologyType,
            release: typing.Optional[str] = None,
    ) -> io.BufferedIOBase:
        if release == self._release:
            return io.BytesIO(self._payload)
        else:
            raise ValueError(f'Unsupported release {release}')


class TestGitHubOntologyStore:

    @pytest.fixture(scope='class')
    def remote_ontology_service(
            self,
            fpath_toy_hpo: str,
    ) -> hpotk.store.RemoteOntologyService:
        with open(fpath_toy_hpo, 'rb') as fh:
            return MockRemoteOntologyService(
                release='v2022-10-05',
                payload=fh.read(),
            )

    @pytest.fixture
    def ontology_store(
            self,
            tmp_path: Path,
            remote_ontology_service: hpotk.store.RemoteOntologyService,
    ) -> hpotk.OntologyStore:
        return hpotk.configure_ontology_store(
            store_dir=str(tmp_path),
            remote_ontology_service=remote_ontology_service,
        )

    def test_load_minimal_hpo(
            self,
            ontology_store: hpotk.OntologyStore,
    ):
        # We start with a clean slate.
        assert len(os.listdir(ontology_store.store_dir)) == 0

        release = 'v2022-10-05'
        hpo = ontology_store.load_minimal_hpo(release=release)

        assert isinstance(hpo, hpotk.MinimalOntology)
        assert hpo.version == release[1:]

        fpath_expected = os.path.join(ontology_store.store_dir, 'HP', f'hp.{release}.json')
        assert os.path.isfile(fpath_expected)

    def test_load_minimal_hpo__invalid_release(
            self,
            ontology_store: hpotk.OntologyStore,
    ):

        release = 'v3400-12-31'
        with pytest.raises(ValueError) as e:
            ontology_store.load_minimal_hpo(release=release)

        # We test that we get whatever exception was raised by the `RemoteOntologyService`.
        assert e.value.args[0] == f'Unsupported release {release}'
