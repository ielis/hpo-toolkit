import abc
import typing
import warnings

from hpotk.model import TermId, Identified

# #####################################################################################################################
# The file describes generic schema for annotations, annotated items, and annotated item containers.
# An example application includes phenotypic features (annotations), diseases or samples (annotated items),
# and OMIM corpus (annotated item containers).
# #####################################################################################################################


class ObservableAnnotation(Identified, metaclass=abc.ABCMeta):
    """
    An identified item with present or absent state.
    """

    @property
    @abc.abstractmethod
    def is_present(self) -> bool:
        """
        :return: `True` if the annotation has been *observed* in the annotated object.
        """
        pass

    @property
    def is_absent(self) -> bool:
        """
        :return: `True` if the annotation has been *excluded* in the annotated object.
        """
        return not self.is_present


ANNOTATION = typing.TypeVar('ANNOTATION', bound=ObservableAnnotation)
"""
A world item annotation with present or absent state.
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


class AnnotatedItemContainer(typing.Generic[ANNOTATED_ITEM], typing.Iterable[ANNOTATED_ITEM], typing.Sized,
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

