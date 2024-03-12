import abc
import enum
import logging
import typing

from hpotk.ontology import MinimalOntology, Ontology


class OntologyType(enum.Enum):
    """
    Enum with the ontologies supported by the :class:`OntologyStore` of the HPO toolkit.
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


class OntologyStore(metaclass=abc.ABCMeta):
    """
    `OntologyStore` stores versions of the supported ontologies.
    """

    def __init__(
            self,
            store_dir: str,
    ):
        self._logger = logging.getLogger(__name__)
        self._store_dir = store_dir

    @abc.abstractmethod
    def load_minimal_ontology(
            self,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ) -> MinimalOntology:
        pass

    @abc.abstractmethod
    def load_ontology(
            self,
            ontology_type: OntologyType,
            release: typing.Optional[str] = None,
    ) -> Ontology:
        pass

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
