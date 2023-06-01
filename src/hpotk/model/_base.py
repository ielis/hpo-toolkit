import abc
import typing
import warnings

from ._term_id import TermId


class Identified(metaclass=abc.ABCMeta):
    """
    An entity that has a CURIE identifier.
    """

    @property
    @abc.abstractmethod
    def identifier(self) -> TermId:
        """
        :return: the identifier of the entity.
        """
        pass


class ObservableFeature(metaclass=abc.ABCMeta):
    """
    `ObservableFeature` represents a feature that can be either in a present or excluded state
    in the investigated item(s).
    """

    @property
    @abc.abstractmethod
    def is_present(self) -> bool:
        """
        :return: `True` if the feature was observed in one or more items.
        """
        pass

    @property
    def is_absent(self) -> bool:
        # REMOVE[v1.0.0]
        warnings.warn("`is_absent` was deprecated and will be removed in v1.0.0. Use `is_excluded` instead",
                      DeprecationWarning, stacklevel=2)
        return self.is_excluded

    @property
    def is_excluded(self) -> bool:
        """
        :return: `True` if the feature was observed in none of the annotated item(s), and therefore, excluded.
        """
        return not self.is_present


class Named(metaclass=abc.ABCMeta):
    """
    An entity that has human-readable name or label.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        :return: the human-readable name of the entity
        """
        pass


class Versioned(metaclass=abc.ABCMeta):
    """
    Base class for entities that may have version.
    """

    @property
    @abc.abstractmethod
    def version(self) -> typing.Optional[str]:
        """
        :return: version `str` or `None` if the version is not available.
        """
        pass


class MetadataAware(metaclass=abc.ABCMeta):
    """
    Base class for entities that have metadata.
    """

    @property
    @abc.abstractmethod
    def metadata(self) -> typing.MutableMapping[str, str]:
        """
        :return: a mapping with entity metadata.
        """
        pass

    def metadata_to_str(self) -> str:
        """
        Dump the metadata to a single string.
        """
        forbidden = {';', '='}
        for k, v in self.metadata.items():
            if any([token in k or token in v for token in forbidden]):
                raise ValueError(f'Metadata contains forbidden characters {forbidden}')

        return ';'.join([f'{k}={v}' for k, v in self.metadata.items()])

    @staticmethod
    def metadata_from_str(value: str) -> typing.Mapping[str, str]:
        """
        Load the metadata from `str` created by `metadata_to_str`.
        """
        data = {}
        for item in value.split(';'):
            k, v = item.split('=')
            data[k] = v
        return data
