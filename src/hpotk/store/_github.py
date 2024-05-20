import io
import json
import logging
import ssl
import typing
from urllib.request import urlopen

import certifi

from ._api import OntologyType, OntologyReleaseService, RemoteOntologyService


ONTOLOGY_CREDENTIALS = {
        OntologyType.HPO: {
            'owner': 'obophenotype',
            'repo': 'human-phenotype-ontology',
        }
    }
"""
The default ontology credentials that only include HPO at the time.
"""


class GitHubOntologyReleaseService(OntologyReleaseService):
    """
    `GitHubOntologyReleaseService` can fetch the ontology tags from GitHub.
    """

    def __init__(
            self,
            timeout: int = 10,
            ontology_credentials: typing.Mapping[OntologyType, typing.Mapping[str, str]] = ONTOLOGY_CREDENTIALS,
    ):
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout
        self._tag_api_url = 'https://api.github.com/repos/{owner}/{repo}/tags'
        self._ctx = ssl.create_default_context(cafile=certifi.where())
        self._ontology_credentials = ontology_credentials

    def fetch_tags(self, ontology_type: OntologyType) -> typing.Iterable[str]:
        if ontology_type not in self._ontology_credentials:
            raise ValueError(
                f'Ontology {ontology_type} not among '
                f'the known ontology credentials {set(self._ontology_credentials.keys())}'
            )
        credentials = self._ontology_credentials[ontology_type]

        return self._get_tag_names(
            owner=credentials['owner'],
            repo=credentials['repo'],
        )

    def _get_tag_names(
            self,
            owner: str,
            repo: str,
    ) -> typing.Iterable[str]:
        tag_url = self._tag_api_url.format(owner=owner, repo=repo)
        self._logger.debug('Pulling tag from %s', tag_url)

        with urlopen(
                tag_url,
                timeout=self._timeout,
                context=self._ctx,
        ) as fh:
            tags = json.load(fh)

        if len(tags) == 0:
            raise ValueError('No tags could be fetched from GitHub tag API')
        else:
            self._logger.debug('Fetched %d tags', len(tags))

        return (tag['name'] for tag in tags)


class GitHubRemoteOntologyService(RemoteOntologyService):
    """
    `GitHubRemoteOntologyService` knows how to fetch ontology data from GitHub.

    The Obographs JSON files are fetched and only HPO is supported as of now.
    """

    def __init__(
            self,
            timeout: int = 10,
            ontology_credentials: typing.Mapping[OntologyType, typing.Mapping[str, str]] = ONTOLOGY_CREDENTIALS,
    ):
        self._logger = logging.getLogger(__name__)
        self._timeout = timeout
        self._ctx = ssl.create_default_context(cafile=certifi.where())
        self._release_url = 'https://github.com/{owner}/{repo}/releases/download/{release}/{ontology_id}.json'
        self._ontology_credentials = ontology_credentials

    def fetch_ontology(
            self,
            ontology_type: OntologyType,
            release: str,
    ) -> io.BufferedIOBase:
        if ontology_type not in self._ontology_credentials:
            raise ValueError(f'Ontology {ontology_type} not among the known ontology credentials')
        credentials = self._ontology_credentials[ontology_type]

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

        return urlopen(
            url,
            timeout=self._timeout,
            context=self._ctx,
        )
