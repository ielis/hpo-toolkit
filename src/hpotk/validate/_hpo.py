import typing

from hpotk.algorithm import get_ancestors
from hpotk.model import Identified
from hpotk.ontology import MinimalOntology
from hpotk.constants.hpo.base import PHENOTYPIC_ABNORMALITY

from ._model import ValidationResult, ValidationResults, ValidationLevel, RuleValidator


class AnnotationPropagationValidator(RuleValidator):
    """
    Validator to check that a sequence of terms does not contain a term and its ancestor.
    """

    def __init__(self, ontology: MinimalOntology):
        self._ontology = ontology

    def validate(self, items: typing.Sequence[Identified]) -> ValidationResults:
        term_ids = {term.identifier for term in items}
        results = []
        for term in items:
            for ancestor in get_ancestors(self._ontology, source=term.identifier, include_source=False):
                if ancestor in term_ids:
                    current_term = self._ontology.get_term(term.identifier)
                    ancestor_term = self._ontology.get_term(ancestor)
                    results.append(
                        ValidationResult(level=ValidationLevel.ERROR,
                                         category='annotation_propagation',
                                         message=f'Terms should not contain both '
                                                 f'{current_term.name} [{current_term.identifier.value}] '
                                                 f'and its ancestor '
                                                 f'{ancestor_term.name}[{ancestor_term.identifier.value}]'))

        return ValidationResults(results)


class PhenotypicAbnormalityValidator(RuleValidator):
    """
    Validator for checking that the term is a phenotypic abnormality
    (a descendant of Phenotypic abnormality HP:0000118).
    """

    def __init__(self, ontology: MinimalOntology):
        self._ontology = ontology

    def validate(self, items: typing.Sequence[Identified]) -> ValidationResults:
        results = []
        for term in items:
            ancestors = get_ancestors(self._ontology, source=term.identifier, include_source=False)
            if PHENOTYPIC_ABNORMALITY not in ancestors:
                current_term = self._ontology.get_term(term.identifier)
                results.append(
                    ValidationResult(
                        level=ValidationLevel.ERROR,
                        category='phenotypic_abnormality_descendant',
                        message=f'{current_term.name} [{current_term.identifier.value}] '
                                f'is not a descendant of Phenotypic abnormality [{PHENOTYPIC_ABNORMALITY}]'
                    )
                )

        return ValidationResults(results)
