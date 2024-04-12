import io
import json
import logging
import typing
from urllib.request import urlopen

from ._api import OntologyType, RemoteOntologyService


class GitHubRemoteOntologyService(RemoteOntologyService):
    """
    `GitHubRemoteOntologyService` knows how to fetch ontology data from GitHub.

    The Obographs JSON files are fetched and only HPO is supported as of now.
    """

    ONTOLOGY_CREDENTIALS = {
        OntologyType.HPO: {
            'owner': 'obophenotype',
            'repo': 'human-phenotype-ontology',
        }
    }

    def __init__(
            self,
            timeout: int = 10,
    ):
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout
        self._tag_api_url = 'https://api.github.com/repos/{owner}/{repo}/tags'
        self._release_url = 'https://github.com/{owner}/{repo}/releases/download/{release}/{ontology_id}.json'

    def fetch_ontology(
            self,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ) -> io.BufferedIOBase:
        if ontology_type not in self.ONTOLOGY_CREDENTIALS:
            raise ValueError(f'Ontology {ontology_type} not among the known ontology credentials')
        credentials = self.ONTOLOGY_CREDENTIALS[ontology_type]

        # Figure out the desired release
        if release is None:
            release = self._fetch_latest_tag_from_github(credentials)
        self._logger.debug('Using %s as the ontology release', release)

        owner = credentials['owner']
        repo = credentials['repo']
        url = self._release_url.format(
            owner=owner,
            repo=repo,
            release=release,
            ontology_id=ontology_type.identifier.lower(),
        )
        self._logger.info('Downloading ontology from %s', url)

        return urlopen(url, timeout=self._timeout)

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

        with urlopen(tag_url, timeout=self._timeout) as r:
            tags = json.load(r)

        if len(tags) == 0:
            raise ValueError('No tags could be fetched from GitHub tag API')
        else:
            self._logger.debug('Fetched %d tags', len(tags))

        return (tag['name'] for tag in tags)
