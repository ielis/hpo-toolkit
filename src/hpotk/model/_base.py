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


class FrequencyAwareFeature(ObservableFeature, metaclass=abc.ABCMeta):
    """
    `FrequencyAwareFeature` entities describe the frequency of a feature in one or more annotated items.

    The simplest case is presence or absence of the feature in a single item, for instance the presence or absence
    of a phenotypic feature, such as hypertension, in a study subject. Another use case is representation
    of the feature frequency in a collection of items, such as presence of a phenotypic feature in a cohort.

    The absolute counts are stored in the `numerator` and `denominator` attributes.

    **IMPORTANT**: the implementor must check the following:
     - the `numerator` must be a non-negative `int`
     - the `denominator` must be a positive `int`

    Use the convenience static method `FrequencyAwareFeature.check_numerator_and_denominator` to check the properties.
    """

    @property
    @abc.abstractmethod
    def numerator(self) -> int:
        """
        :return: a non-negative `int` representing the count of annotated items where the annotation was present.
        """
        pass

    @property
    @abc.abstractmethod
    def denominator(self) -> int:
        """
        :return: a positive `int` representing the total count of annotated items investigated
        for presence/absence of an annotation.
        """
        pass

    def frequency(self) -> float:
        """

        :return: a `float` in range :math:`[0, 1]` representing the ratio of the annotation in the annotated item(s).
        """
        return self.numerator / self.denominator

    @property
    def is_present(self) -> bool:
        """
        :return: `True` if the annotation was observed in one or more items.
        """
        return self.numerator != 0

    @property
    def is_excluded(self) -> bool:
        """
        :return: `True` if the annotation was observed in none of the annotated item(s), and therefore, excluded.
        """
        return self.numerator == 0

    @staticmethod
    def check_numerator_and_denominator(numerator: int, denominator: int) -> None:
        """
        Check if the `numerator` and `denominator` satisfy the requirements described in :class:`FrequencyAwareFeature`.

        :return: `None` if the check passes or raises a `ValueError` if the `numerator` or `denominator` contain
          invalid values.
        """
        if not isinstance(numerator, int) or numerator < 0:
            raise ValueError(f'Numerator {numerator} must be a non-negative `int`')
        if not isinstance(denominator, int) or denominator <= 0:
            raise ValueError(f'Denominator {denominator} must be a positive `int`')


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
