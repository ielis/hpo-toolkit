import abc
import typing
import warnings

from hpotk.model import Identified, FrequencyAwareFeature, Versioned, CURIE_OR_TERM_ID_OR_IDENTIFIED
from hpotk.model import TermId
from hpotk.util import extract_term_id


# #####################################################################################################################
# The file describes generic schema for annotations, annotated items, and annotated item containers.
# An example application includes phenotypic features (annotations), diseases or samples (annotated items),
# and OMIM corpus (annotated item containers).
# #####################################################################################################################


class AnnotationBase(Identified, FrequencyAwareFeature):
    pass


ANNOTATION = typing.TypeVar("ANNOTATION", bound=AnnotationBase)
"""
A world item annotation with an identifier and present or excluded state.
"""


class AnnotatedItem(
    typing.Generic[ANNOTATION],
    Identified,
    metaclass=abc.ABCMeta,
):
    """
    An item that can be annotated with ontology terms. For instance, a disease can be annotated with phenotypic features,
    items from HPO ontology.
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
    
    def annotation_by_id(
        self,
        query: CURIE_OR_TERM_ID_OR_IDENTIFIED,
    ) -> typing.Optional[ANNOTATION]:
        """
        Find the annotation identified by the `query`.

        Performs a linear search and finds the *first* match.

        :param query: a `str` with CURIE, an :class:`~hpotk.TermId`, or an :class:`~hpotk.model.Identified` item (an item with an identifier).
        :return: an annotation or `None` if no such annotation exists.
        """
        term_id = extract_term_id(query)
        for ann in self.annotations:
            if ann.identifier == term_id:
                return ann
        return None


ANNOTATED_ITEM = typing.TypeVar("ANNOTATED_ITEM", bound=AnnotatedItem)
"""
World item that is annotated with an :class:`ANNOTATION`.
"""


class AnnotatedItemContainer(
    typing.Generic[ANNOTATED_ITEM],
    typing.Iterable[ANNOTATED_ITEM],
    typing.Sized,
    Versioned,
    metaclass=abc.ABCMeta,
):
    """
    Container for items that can be annotated with ontology terms.

    For instance, if OMIM disease is an item type and phenotypic feature is the annotation type,
    then a corpus of OMIM diseases corresponds to a container of annotated items.
    """

    @property
    def items(self) -> typing.Collection[ANNOTATED_ITEM]:
        """
        :return: an iterable over container items.
        """
        # REMOVE(v1.0.0)
        warnings.warn(
            "`items` property has been deprecated and will be removed in v1.0.0. "
            "Iterate directly over the container.",
            DeprecationWarning,
            stacklevel=2,
        )
        return list(self)

    def item_ids(self) -> typing.Iterable[TermId]:
        """
        :return: an iterable over all item identifiers.
        """
        return (item.identifier for item in self)
