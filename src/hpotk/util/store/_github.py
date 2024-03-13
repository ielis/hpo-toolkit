import json
import os
import typing
import urllib
from urllib.request import urlopen, HTTPError

from hpotk.ontology import Ontology, MinimalOntology
from hpotk.ontology.load.obographs import load_minimal_ontology, load_ontology
from ._api import OntologyType, OntologyStore


class GitHubOntologyStore(OntologyStore):
    """
    `GitHubOntologyStore` fetches an Obographs ontology JSON from GitHub.
    """

    ONTOLOGY_CREDENTIALS = {
        OntologyType.HPO: {
            'owner': 'obophenotype',
            'repo': 'human-phenotype-ontology',
        }
    }

    def __init__(
            self,
            store_dir: str,
            timeout: int = 10,
    ):
        super().__init__(store_dir=store_dir)
        self._timeout = timeout
        self._tag_api_url = 'https://api.github.com/repos/{owner}/{repo}/tags'
        self._release_url = 'https://github.com/{owner}/{repo}/releases/download/{release}/{ontology_id}.json'

    def load_minimal_ontology(self, ontology_type: OntologyType,
                              release: typing.Optional[str] = None) -> MinimalOntology:
        return self._impl_load_ontology(
            load_minimal_ontology,
            ontology_type,
            release,
        )

    def load_ontology(
            self,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ) -> Ontology:
        return self._impl_load_ontology(
            load_ontology,
            ontology_type,
            release,
        )

    def _impl_load_ontology(
            self,
            loader_func,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ):
        if ontology_type not in self.ONTOLOGY_CREDENTIALS:
            raise ValueError(f'Ontology {ontology_type} not among the known ontology credentials')
        credentials = self.ONTOLOGY_CREDENTIALS[ontology_type]

        # Figure out the desired release
        if release is None:
            release = self._fetch_latest_tag_from_github(credentials)
        self._logger.debug('Using %s as the ontology release', release)

        # Check if we have the release in the local storage
        # and download the JSON file if not.
        fpath_ontology = self._download_ontology_if_missing(credentials, ontology_type.identifier, release)

        # Load the ontology
        return loader_func(fpath_ontology)

    def _download_ontology_if_missing(
            self,
            credentials: typing.Mapping[str, str],
            ontology_id: str,
            release: str,
    ) -> str:
        fdir_ontology = os.path.join(self.store_dir, ontology_id)
        fpath_ontology = os.path.join(fdir_ontology, f'{ontology_id.lower()}.{release}.json')
        if not os.path.isfile(fpath_ontology):
            os.makedirs(fdir_ontology, exist_ok=True)
            owner = credentials['owner']
            repo = credentials['repo']
            url = self._release_url.format(
                owner=owner,
                repo=repo,
                release=release,
                ontology_id=ontology_id.lower(),
            )
            self._logger.info('Downloading ontology from %s', url)
            self._logger.info('Storing the ontology at %s', fpath_ontology)
            try:
                with urlopen(url, timeout=self._timeout) as response, open(fpath_ontology, 'wb') as fh_ontology:
                    fh_ontology.write(response.read())
            except HTTPError as he:
                if he.code == 404:
                    # Most likely a non-existing release.
                    raise ValueError(f'Could not find {release} on GitHub')
                else:
                    # Another error.
                    raise he
            self._logger.info('Download complete')

        return fpath_ontology

    def _fetch_latest_tag_from_github(self, credentials: typing.Mapping[str, str]):
        self._logger.debug('Release unset, getting the latest')
        tag_names = self._get_tag_names(
            owner=credentials['owner'],
            repo=credentials['repo'],
        )
        # We assume lexicographic sorting of the tags
        return max(tag_names)

    def _get_tag_names(self, owner: str, repo: str) -> typing.Iterable[str]:
        tag_url = self._tag_api_url.format(owner=owner, repo=repo)
        self._logger.debug('Pulling tag from %s', tag_url)

        with urllib.request.urlopen(tag_url, timeout=self._timeout) as r:
            tags = json.load(r)

        if len(tags) == 0:
            raise ValueError('No tags could be fetched from GitHub tag API')
        else:
            self._logger.debug('Fetched %d tags', len(tags))

        return [tag['name'] for tag in tags]
