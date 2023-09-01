import abc
import typing

from hpotk.model import Identified, TermId
from hpotk.ontology import MinimalOntology
from hpotk.constants.hpo.base import PHENOTYPIC_ABNORMALITY
from hpotk.util import validate_instance

from ._model import ValidationResult, ValidationResults, ValidationLevel, RuleValidator
from ._util import SimpleFeature

T = typing.TypeVar('T', SimpleFeature, TermId)


class BaseOntologyRuleValidator(RuleValidator, metaclass=abc.ABCMeta):

    def __init__(self, hpo: MinimalOntology):
        self._hpo = validate_instance(hpo, MinimalOntology, 'hpo')

    def _primary_term_id(self, feature: T) -> typing.Optional[T]:
        """
        Update the term ID of the `feature` to the primary term ID in case the current term ID is obsolete.
        """
        if isinstance(feature, SimpleFeature):
            current_id = self._hpo.get_term(feature.identifier)
            if current_id is None:
                return None
            if current_id.identifier != feature.identifier:
                # Update to the primary term ID.
                feature.identifier = current_id.identifier
            return feature
        elif isinstance(feature, TermId):
            current = self._hpo.get_term(feature)
            return None if current is None else current.identifier
        else:
            raise ValueError(f'feature must be either a `TermId` or `SimpleFeature` but was {type(feature)}')


class AnnotationPropagationValidator(BaseOntologyRuleValidator):
    """
    Validator to check that a sequence of terms, when interpreted together, does not violate the annotation propagation
    rule.

    More formally, the terms must not satisfy the following:

    * terms must not contain a present term and its present or excluded ancestor
    * terms must not contain an excluded term and its excluded ancestor

    Violation of annotation propagation rule produces an :class:`ValidationLevel.ERROR`.

    The validator replaces obsolete term IDs with the current term IDs before performing the validation.

    :param ontology: HPO represented as :class:`hpotk.ontology.MinimalOntology`.
    """

    def __init__(self, ontology: MinimalOntology):
        super().__init__(ontology)

    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        stateful_features: typing.Collection[SimpleFeature] = {
            self._primary_term_id(self._extract_stateful_feature(item))
            for item in items
            if item is not None
        }
        results = []
        for feature in stateful_features:
            if feature.is_present:
                # A present feature cannot coexist with a present or excluded ancestor.
                for anc in self._hpo.graph.get_ancestors(feature):
                    if any(anc == sf.identifier for sf in stateful_features):
                        current_term = self._hpo.get_term(feature.identifier)
                        term = self._hpo.get_term(anc)
                        results.append(
                            ValidationResult(level=ValidationLevel.ERROR,
                                             category='annotation_propagation',
                                             message=f'Terms should not contain both present '
                                                     f'{current_term.name} [{current_term.identifier.value}] '
                                                     f'and its present or excluded ancestor '
                                                     f'{term.name} [{term.identifier.value}]'))
            else:
                # An excluded feature cannot coexist with an excluded ancestor.
                for anc in self._hpo.graph.get_ancestors(feature):
                    # We only check excluded ancestors here since presence of an ancestor is allowed
                    # for an excluded feature.
                    if any(anc == sf.identifier for sf in stateful_features if sf.is_excluded):
                        current_term = self._hpo.get_term(feature.identifier)
                        term = self._hpo.get_term(anc)
                        results.append(
                            ValidationResult(level=ValidationLevel.ERROR,
                                             category='annotation_propagation',
                                             message=f'Terms should not contain both excluded '
                                                     f'{current_term.name} [{current_term.identifier.value}] '
                                                     f'and its present or excluded ancestor '
                                                     f'{term.name} [{term.identifier.value}]'))

        return ValidationResults(results)


class PhenotypicAbnormalityValidator(BaseOntologyRuleValidator):
    """
    Validator for checking that the term is a phenotypic abnormality
    (a descendant of `Phenotypic abnormality <https://hpo.jax.org/app/browse/term/HP:0000118>`_ [HP:0000118]).

    Presence of a term that is not a descendant of Phenotypic abnormality is a :class:`ValidationLevel.WARNING`.

    The validator replaces obsolete term IDs with the current term IDs before performing the validation.

    :param ontology: HPO represented as :class:`hpotk.ontology.MinimalOntology`.
    """

    def __init__(self, ontology: MinimalOntology):
        super().__init__(ontology)

    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        results = []
        for item in items:
            primary = self._primary_term_id(self._extract_stateful_feature(item))
            if primary is None:
                # Unable to get the primary term ID. Handling items with obsolete IDs is not the responsibility
                # of this validator
                continue
            if not any(PHENOTYPIC_ABNORMALITY == anc for anc in self._hpo.graph.get_ancestors(primary)):
                item = self._hpo.get_term(primary.identifier)
                results.append(
                    ValidationResult(
                        level=ValidationLevel.WARNING,
                        category='phenotypic_abnormality_descendant',
                        message=f'{item.name} [{item.identifier.value}] '
                                f'is not a descendant of Phenotypic abnormality [{PHENOTYPIC_ABNORMALITY.value}]'
                    )
                )

        return ValidationResults(results)


class ObsoleteTermIdsValidator(BaseOntologyRuleValidator):
    """
    `ObsoleteTermIdsValidator` points out usage of obsolete term ids in `items`.

    Presence of an obsolete term ID is a :class:`ValidationLevel.WARNING`.

    :param ontology: HPO represented as :class:`hpotk.ontology.MinimalOntology`.
    """

    def __init__(self, ontology: MinimalOntology):
        super().__init__(ontology)

    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        results = []
        for item in items:
            sf = self._extract_stateful_feature(item)
            current = sf.identifier  # cache the ID since _primary_term_id can update in place.
            primary = self._primary_term_id(sf)
            if primary.identifier != current:
                current_term = self._hpo.get_term(sf.identifier)
                results.append(
                    ValidationResult(
                        level=ValidationLevel.WARNING,
                        category='obsolete_term_id_is_used',
                        message=f'Using the obsolete {current.value} instead of {primary.identifier.value} '
                                f'for {current_term.name}'
                    )
                )

        return ValidationResults(results)
