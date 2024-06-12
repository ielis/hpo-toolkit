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
            raise ValueError(f"Unsupported release {release}")


class TestGitHubOntologyStore:

    @pytest.fixture(scope="class")
    def remote_ontology_service(
        self,
        fpath_toy_hpo: str,
    ) -> hpotk.store.RemoteOntologyService:
        with open(fpath_toy_hpo, "rb") as fh:
            return MockRemoteOntologyService(
                release="v2022-10-05",
                payload=fh.read(),
            )

    @pytest.fixture
    def ontology_store(
        self,
        tmp_path: Path,
        remote_ontology_service: hpotk.store.RemoteOntologyService,
    ) -> hpotk.OntologyStore:
        ontology_release_service = hpotk.store.GitHubOntologyReleaseService()
        return hpotk.store.OntologyStore(
            store_dir=str(tmp_path),
            ontology_release_service=ontology_release_service,
            remote_ontology_service=remote_ontology_service,
        )

    def test_load_minimal_hpo(
        self,
        ontology_store: hpotk.OntologyStore,
    ):
        # We start with a clean slate.
        assert len(os.listdir(ontology_store.store_dir)) == 0

        release = "v2022-10-05"
        hpo = ontology_store.load_minimal_hpo(release=release)

        assert isinstance(hpo, hpotk.MinimalOntology)
        assert hpo.version == release[1:]

        fpath_expected = os.path.join(
            ontology_store.store_dir, "HP", f"hp.{release}.json"
        )
        assert os.path.isfile(fpath_expected)

    def test_load_minimal_hpo__invalid_release(
        self,
        ontology_store: hpotk.OntologyStore,
    ):

        release = "v3400-12-31"
        with pytest.raises(ValueError) as e:
            ontology_store.load_minimal_hpo(release=release)

        # We test that we get whatever exception was raised by the `RemoteOntologyService`.
        assert e.value.args[0] == f"Unsupported release {release}"

    @pytest.mark.parametrize(
        "ontology_type,release,expected_fname",
        [
            (hpotk.store.OntologyType.HPO, "v2024-04-19", "hp.v2024-04-19.json"),
            (hpotk.store.OntologyType.HPO, "v2024-04-26", "hp.v2024-04-26.json"),
        ],
    )
    def test_resolve_store_path(
        self,
        ontology_store: hpotk.OntologyStore,
        ontology_type: hpotk.store.OntologyType,
        release: str,
        expected_fname: str,
    ):
        actual = ontology_store.resolve_store_path(
            ontology_type=ontology_type, release=release
        )

        expected = os.path.join(
            ontology_store.store_dir, ontology_type.identifier, expected_fname
        )
        assert actual == expected

    def test_clear__everything(
        self,
        ontology_store: hpotk.OntologyStore,
    ):
        store_dir = Path(ontology_store.store_dir)
        
        stuff = os.listdir(store_dir)
        assert len(stuff) == 0, "The store directory is empty upon start"
        
        TestGitHubOntologyStore.initialize_store_dir(store_dir)

        stuff = os.listdir(store_dir)
        assert len(stuff) == 3, 'The store directory now includes two folders and one file'

        ontology_store.clear()

        stuff = os.listdir(store_dir)
        assert len(stuff) == 0, "The store directory is empty after clearing everything"

    @pytest.mark.parametrize(
        'resource',
        [
            hpotk.OntologyType.HPO,
        ],
    )
    def test_clear__ontology_type(
        self,
        resource: hpotk.OntologyType,
        ontology_store: hpotk.OntologyStore,
    ):
        store_dir = Path(ontology_store.store_dir)
        stuff = os.listdir(store_dir)

        assert len(stuff) == 0, "The store directory is empty upon start"

        TestGitHubOntologyStore.initialize_store_dir(store_dir)

        stuff = os.listdir(store_dir)
        assert len(stuff) == 3, 'The store directory now includes two folders and one file'

        ontology_store.clear(resource)

        stuff = os.listdir(store_dir)
        assert len(stuff) == 2


    @staticmethod
    def initialize_store_dir(store_dir: Path):
        # Make a few folders and files
        store_dir.joinpath('joe.txt').touch()  # a file
        
        hp_path = store_dir.joinpath('HP')  # a folder
        os.mkdir(hp_path)
        hp_path.joinpath('a.txt').touch()
        hp_path.joinpath('b.txt').touch()

        mondo_path = store_dir.joinpath('MONDO')  # another folder
        os.mkdir(mondo_path)
        mondo_path.joinpath('x.txt').touch()
        mondo_path.joinpath('y.txt').touch()

@pytest.mark.online
class TestGitHubOntologyReleaseService:

    @pytest.fixture
    def ontology_release_service(self) -> hpotk.store.OntologyReleaseService:
        return hpotk.store.GitHubOntologyReleaseService()

    def test_ontology_release_service(
        self,
        ontology_release_service: hpotk.store.OntologyReleaseService,
    ):
        tag_iter = ontology_release_service.fetch_tags(hpotk.store.OntologyType.HPO)

        assert tag_iter is not None

        tags = set(tag_iter)

        expected = {  # As of May 20th, 2024
            "v2020-08-11",
            "v2020-10-12",
            "v2020-12-07",
            "v2021-02-08",
            "v2021-04-13",
            "v2021-06-08",
            "v2021-06-13",
            "v2021-08-02",
            "v2021-10-10",
            "v2022-01-27",
            "v2022-02-14",
            "v2022-04-14",
            "v2022-06-11",
            "v2022-10-05",
            "v2022-12-15",
            "v2023-01-27",
            "v2023-04-05",
            "v2023-06-06",
            "v2023-06-17",
            "v2023-07-21",
            "v2023-09-01",
            "v2023-10-09",
            "v2024-01-11",
            "v2024-01-16",
            "v2024-02-08",
            "v2024-03-06",
            "v2024-04-03",
            "v2024-04-04",
            "v2024-04-19",
            "v2024-04-26",
        }
        assert all(tag in tags for tag in expected)
