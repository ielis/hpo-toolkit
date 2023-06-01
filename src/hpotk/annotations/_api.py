import abc
import typing
import warnings

from hpotk.model import Identified, ObservableFeature, Versioned
from hpotk.model import TermId


# #####################################################################################################################
# The file describes generic schema for annotations, annotated items, and annotated item containers.
# An example application includes phenotypic features (annotations), diseases or samples (annotated items),
# and OMIM corpus (annotated item containers).
# #####################################################################################################################


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


class AnnotationBase(Identified, FrequencyAwareFeature, metaclass=abc.ABCMeta):
    pass


ANNOTATION = typing.TypeVar('ANNOTATION', bound=AnnotationBase)
"""
A world item annotation with an identifier and present or excluded state.
"""


class AnnotatedItem(typing.Generic[ANNOTATION], metaclass=abc.ABCMeta):
    """
    A world item with annotations. For instance, a disease annotated by phenotypic features.
    """

    @property
    @abc.abstractmethod
    def annotations(self) -> typing.Collection[ANNOTATION]:
        """
        :return: a collection of :class:`ANNOTATION` objects for the annotated item.
        """
        pass

    def present_annotations(self) -> typing.Iterable[ANNOTATION]:
        """
        :return: an iterable over *present* annotations.
        """
        return filter(lambda a: a.is_present, self.annotations)

    def absent_annotations(self) -> typing.Iterable[ANNOTATION]:
        """
        :return: an iterable over *absent* annotations.
        """
        return filter(lambda a: a.is_absent, self.annotations)


ANNOTATED_ITEM = typing.TypeVar('ANNOTATED_ITEM', bound=AnnotatedItem)
"""
World item that is annotated with an :class:`ANNOTATION`.
"""


class AnnotatedItemContainer(typing.Generic[ANNOTATED_ITEM],
                             typing.Iterable[ANNOTATED_ITEM],
                             typing.Sized,
                             Versioned,
                             metaclass=abc.ABCMeta):
    """
    Container for annotated items.

    For instance, if OMIM disease is an item type and phenotypic feature is the annotation type,
    then a corpus of OMIM diseases corresponds to a container of annotated items.
    """

    @property
    def items(self) -> typing.Collection[ANNOTATED_ITEM]:
        """
        :return: an iterable over container items.
        """
        # REMOVE(v1.0.0)
        warnings.warn(f'`items` property has been deprecated and will be removed in v1.0.0. '
                      f'Iterate directly over the container.',
                      DeprecationWarning, stacklevel=2)
        return list(self)

    def item_ids(self) -> typing.Iterable[TermId]:
        """
        :return: an iterable over all item identifiers.
        """
        return map(lambda item: item.identifier, self)

