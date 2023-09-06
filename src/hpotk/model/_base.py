import abc
import typing
import warnings

from ._term_id import TermId


class Identified(metaclass=abc.ABCMeta):
    """
    An entity that has an identifier in form of a :class:`TermId`.
    """

    @property
    @abc.abstractmethod
    def identifier(self) -> TermId:
        """
        Get the identifier.
        """
        pass


class ObservableFeature(metaclass=abc.ABCMeta):
    """
    `ObservableFeature` represents a feature that can be either in a *present* or an *excluded* state
    in the investigated item(s).

    The simplest case is the presence or absence of a phenotypic feature, such as hexadactyly, in a study subject.
    """

    @property
    @abc.abstractmethod
    def is_present(self) -> bool:
        """
        Test if the feature was observed in one or more items.

        :return: `True` if the feature was observed in one or more items.
        """
        pass

    @property
    def is_absent(self) -> bool:
        """
        Test if the feature is excluded.

        .. deprecated:: 0.2.1
          Use :py:func:`is_excluded` instead.

        """
        # REMOVE[v1.0.0]
        warnings.warn("`is_absent` was deprecated and will be removed in v1.0.0. Use `is_excluded` instead",
                      DeprecationWarning, stacklevel=2)
        return self.is_excluded

    @property
    def is_excluded(self) -> bool:
        """
        Test if the feature was not observed in any of the items.

        :return: `True` if the feature was observed in *none* of the annotated item(s), and was, therefore, excluded.
        """
        return not self.is_present


class FrequencyAwareFeature(ObservableFeature, metaclass=abc.ABCMeta):
    """
    `FrequencyAwareFeature` entities describe the frequency of a feature in one or more annotated items.

    This is on top of the dichotomous state of :class:`ObservableFeature`, where the feature is present or excluded.

    For instance, we can represent the feature frequency in a collection of items, such as presence of
    a phenotypic feature, such as hexadactyly, in a cohort.

    The absolute counts are accessible via `numerator` and `denominator` properties.

    **IMPORTANT**: the implementor must ensure the following invariants:

     * the `numerator` must be a non-negative `int`
     * the `denominator` must be a positive `int`

    Use the convenience static method :py:func:`check_numerator_and_denominator` to check
    the invariants.
    """

    @property
    @abc.abstractmethod
    def numerator(self) -> int:
        """
        Get the numerator, a non-negative `int` representing the count of annotated items where the annotation
        was present.
        """
        pass

    @property
    @abc.abstractmethod
    def denominator(self) -> int:
        """
        Get the denominator, a positive `int` representing the total count of annotated items investigated
        for presence/absence of an annotation.
        """
        pass

    def frequency(self) -> float:
        """
        Get a `float` in range :math:`[0, 1]` representing the ratio of the annotation in the annotated item(s).
        """
        return self.numerator / self.denominator

    @property
    def is_present(self) -> bool:
        return self.numerator != 0

    @property
    def is_excluded(self) -> bool:
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
    A mixin for the entities that have human-readable name or a label.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        Get the label.
        """
        pass


class Versioned(metaclass=abc.ABCMeta):
    """
    A mixin for the entities that may have version.
    """

    @property
    @abc.abstractmethod
    def version(self) -> typing.Optional[str]:
        """
        Get a version `str` or `None` if the version is not available.
        """
        pass


class MetadataAware(metaclass=abc.ABCMeta):
    """
    A mixin for the entities that have metadata.
    """

    @property
    @abc.abstractmethod
    def metadata(self) -> typing.MutableMapping[str, str]:
        """
        Get a mapping with entity metadata.
        """
        pass

    def metadata_to_str(self) -> str:
        """
        Dump the metadata to a `str`.
        """
        forbidden = {';', '='}
        for k, v in self.metadata.items():
            if any([token in k or token in v for token in forbidden]):
                raise ValueError(f'Metadata contains forbidden characters {forbidden}')

        return ';'.join([f'{k}={v}' for k, v in self.metadata.items()])

    @staticmethod
    def metadata_from_str(value: str) -> typing.Mapping[str, str]:
        """
        Load the metadata from `str` created by :py:func:`metadata_to_str`.
        """
        data = {}
        for item in value.split(';'):
            k, v = item.split('=')
            data[k] = v
        return data
