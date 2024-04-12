import abc
import enum
import io
import logging
import os
import typing

from hpotk.ontology import MinimalOntology, Ontology
from hpotk.ontology.load.obographs import load_minimal_ontology, load_ontology
from hpotk.util import validate_instance


class OntologyType(enum.Enum):
    """
    Enum with the ontologies supported by the :class:`OntologyStore`.
    """

    HPO = 'HPO', 'HP'
    """
    Human Phenotype Ontology.
    """

    def __new__(cls, *args, **kwargs):
        obj = object.__new__(cls)
        obj._value_ = args[0]
        return obj

    def __init__(self, _: str, identifier: str):
        self._id_ = identifier

    @property
    def identifier(self) -> str:
        """
        Get a `str` with the ontology identifier (e.g. ``HP`` for HPO).
        """
        return self._id_


class RemoteOntologyService(metaclass=abc.ABCMeta):
    """
    `RemoteOntologyService` knows how to open a :class:`typing.BinaryIO`
    for reading content of an `ontology_type` of a particular `release`.
    """

    @abc.abstractmethod
    def fetch_ontology(
            self,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ) -> io.BufferedIOBase:
        """
        Open a connection for reading bytes of the `ontology_type` from a remote resource.

        :param ontology_type: the desired ontology kind, e.g. :class:`OntologyType.HPO`.
        :param release: a `str` with the desired ontology release or `None` if the latest release should be fetched.
        :return: a binary IO for reading the ontology data.
        """
        pass


class OntologyStore:
    """
    `OntologyStore` stores versions of the supported ontologies.
    """

    def __init__(
            self,
            store_dir: str,
            remote_ontology_service: RemoteOntologyService,
    ):
        self._logger = logging.getLogger(__name__)
        self._store_dir = store_dir
        self._remote_ontology_service = validate_instance(
            remote_ontology_service, RemoteOntologyService, 'remote_ontology_service')

    def load_minimal_ontology(
            self,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ) -> MinimalOntology:
        """
        Load a `release` of a given `ontology_type` as a minimal ontology.

        :param ontology_type: the desired ontology type, see :class:`OntologyType` for a list of supported ontologies.
        :param release: a `str` with the ontology release tag or `None` if the latest ontology should be fetched.
        :return: a minimal ontology.
        """
        return self._impl_load_ontology(
            load_minimal_ontology,
            ontology_type,
            release,
        )

    @abc.abstractmethod
    def load_ontology(
            self,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ) -> Ontology:
        """
        Load a `release` of a given `ontology_type` as an ontology.

        :param ontology_type: the desired ontology type, see :class:`OntologyType` for a list of supported ontologies.
        :param release: a `str` with the ontology release tag or `None` if the latest ontology should be fetched.
        :return: an ontology.
        """
        return self._impl_load_ontology(
            load_ontology,
            ontology_type,
            release,
        )

    @property
    def store_dir(self) -> str:
        """
        Get a `str` with a platform specific absolute path to the data directory.

        The data directory points to `$HOME/.hpo-toolkit` on UNIX and `$HOME/hpo-toolkit` on Windows.
        The folder is created if it does not exist.
        """
        return self._store_dir

    def load_minimal_hpo(
            self,
            release: typing.Optional[str] = None,
    ) -> MinimalOntology:
        """
        A convenience method for loading a specific HPO release.

        :param release: an optional `str` with the desired HPO release (if `None`, the latest HPO will be provided).
        :return: a :class:`hpotk.MinimalOntology` with the HPO data.
        """
        return self.load_minimal_ontology(OntologyType.HPO, release=release)

    def load_hpo(
            self,
            release: typing.Optional[str] = None,
    ) -> Ontology:
        """
        A convenience method for loading a specific HPO release.

        :param release: an optional `str` with the desired HPO release (if `None`, the latest HPO will be provided).
        :return: a :class:`hpotk.Ontology` with the HPO data.
        """
        return self.load_ontology(OntologyType.HPO, release=release)

    def _impl_load_ontology(
            self,
            loader_func,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ):
        fdir_ontology = os.path.join(self.store_dir, ontology_type.identifier)
        fpath_ontology = os.path.join(fdir_ontology, f'{ontology_type.identifier.lower()}.{release}.json')

        # Download ontology if missing.
        if not os.path.isfile(fpath_ontology):
            os.makedirs(fdir_ontology, exist_ok=True)
            with self._remote_ontology_service.fetch_ontology(ontology_type, release) as response, open(fpath_ontology, 'wb') as fh_ontology:
                fh_ontology.write(response.read())

            self._logger.info('Stored the ontology at %s', fpath_ontology)

        # Load the ontology
        return loader_func(fpath_ontology)
