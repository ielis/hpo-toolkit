import os
import platform
import re
import typing
from pathlib import Path

from ._api import OntologyStore, RemoteOntologyService
from ._github import GitHubRemoteOntologyService


def configure_ontology_store(
        store_dir: typing.Optional[str] = None,
        remote_ontology_service: RemoteOntologyService = GitHubRemoteOntologyService(),
) -> OntologyStore:
    """
    Configure and create the default ontology store.

    :param store_dir: a `str` pointing to an existing directory for caching the ontology files
      or `None` if the platform-specific default folder should be used.
    :param remote_ontology_service: a :class:`RemoteOntologyService` responsible for fetching
      the ontology data from a remote location if we do not have the data locally.
    :returns: an :class:`OntologyStore`.
    :raises: `ValueError` if something goes wrong.
    """
    if store_dir is None:
        store_dir = get_default_ontology_store_dir()
    else:
        if not os.path.isdir(store_dir):
            raise ValueError(f'`store_dir` must point to an existing directory')
    return OntologyStore(
        store_dir=store_dir,
        remote_ontology_service=remote_ontology_service,
    )


def get_default_ontology_store_dir() -> str:
    """
    Get a platform specific absolute path to the data directory.

    The data directory points to `$HOME/.hpo-toolkit` on UNIX and `$HOME/hpo-toolkit` on Windows.
    The folder is created if it does not exist.
    """
    ps = platform.system()

    if re.match('(linux)|(darwin)', ps, re.IGNORECASE):
        store_dir_name = '.hpo-toolkit'
    elif re.match('windows', ps, re.IGNORECASE):
        store_dir_name = 'hpo-toolkit'
    else:
        raise ValueError(f'Unsupported platform {ps}')

    dir_name = os.path.join(Path.home(), store_dir_name)

    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)

    return dir_name
