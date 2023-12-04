import os
import typing

import pytest
from pkg_resources import resource_filename

import hpotk
from hpotk.model import Identified, ObservableFeature, TermId
from hpotk.ontology.load.obographs import load_minimal_ontology
from hpotk.validate import ValidationResult, ValidationLevel
from hpotk.validate import AnnotationPropagationValidator, PhenotypicAbnormalityValidator, ObsoleteTermIdsValidator

TOY_HPO = resource_filename(__name__, os.path.join('data', 'hp.toy.json'))


class SimpleFeature(Identified, ObservableFeature):

    def __init__(self, curie: str, status: bool):
        self._id = TermId.from_curie(curie)
        self._status = status

    @property
    def identifier(self) -> TermId:
        return self._id

    @property
    def is_present(self) -> bool:
        return self._status


class TestBaseRuleValidator:

    @pytest.fixture
    def toy_hpo(self) -> hpotk.MinimalOntology:
        return load_minimal_ontology(TOY_HPO)

    @pytest.fixture
    def example_terms(self) -> typing.Sequence[SimpleFeature]:
        return [SimpleFeature('HP:0001166', True),  # Arachnodactyly
                SimpleFeature('HP:0001250', True),  # Seizure
                SimpleFeature('HP:0032648', True),  # Tubularization of Bowman capsule
                SimpleFeature('HP:0000805', False)  # excluded Enuresis
                ]


class TestAnnotationPropagationValidator(TestBaseRuleValidator):

    @pytest.fixture
    def validator(self, toy_hpo: hpotk.MinimalOntology) -> AnnotationPropagationValidator:
        return AnnotationPropagationValidator(toy_hpo)

    def test_empty_input_is_allowed(self, validator: AnnotationPropagationValidator):
        results = validator.validate([])
        assert results.is_ok()

    def test_ok_input_produces_no_errors(self, validator: AnnotationPropagationValidator,
                                         example_terms: typing.Sequence[SimpleFeature]):
        results = validator.validate(example_terms)
        assert results.is_ok()

    def test_obsolete_ancestor_produces_error(self, validator: AnnotationPropagationValidator,
                                              example_terms: typing.Sequence[SimpleFeature]):
        example_terms = list(example_terms)
        example_terms.append(TermId.from_curie('HP:0006010'))

        results = validator.validate(example_terms)

        assert not results.is_ok()
        assert results.results[0] == ValidationResult(level=ValidationLevel.ERROR, category='annotation_propagation',
                                                      message='Terms should not contain both present Arachnodactyly [HP:0001166] '
                                                              f'and its present or excluded ancestor Long fingers [HP:0100807]')

    @pytest.mark.parametrize('ancestor_curie, ancestor_status, base_curie, base_status',
                             (
                                     # present Long fingers vs. present Arachnodactyly
                                     ("HP:0100807", True, 'HP:0001166', True),

                                     # excluded Long fingers vs. present Arachnodactyly
                                     ("HP:0100807", False, 'HP:0001166', True),

                                     # The case is commented out since it is possible to have some abnormality but excluded specific abnormality
                                     # ("HP:0000014", True, 'HP:0000805', False),  # present Abnormality of the bladder vs. excluded Enuresis

                                     # excluded Abnormality of the bladder vs. excluded Enuresis
                                     ("HP:0000014", False, 'HP:0000805', False),
                             ))
    def test_ancestor_presence_produces_error(self, ancestor_curie, ancestor_status, base_curie, base_status,
                                              toy_hpo: hpotk.MinimalOntology, validator: AnnotationPropagationValidator,
                                              example_terms: typing.Sequence[SimpleFeature]):
        example_terms = list(example_terms)
        example_terms.append(SimpleFeature(ancestor_curie, ancestor_status))

        results = validator.validate(example_terms)

        assert not results.is_ok()
        assert 1 == len(results.results)
        first = results.results[0]
        assert ValidationLevel.ERROR == first.level
        assert 'annotation_propagation' == first.category

        state = 'present' if base_status else 'excluded'
        assert (f'Terms should not contain both {state} '
                f'{toy_hpo.get_term(base_curie).name} [{toy_hpo.get_term(base_curie).identifier.value}] '
                f'and its present or excluded ancestor '
                f'{toy_hpo.get_term(ancestor_curie).name} [{ancestor_curie}]' == first.message)


class TestPhenotypicAbnormalityValidator(TestBaseRuleValidator):

    @pytest.fixture
    def validator(self, toy_hpo: hpotk.MinimalOntology) -> PhenotypicAbnormalityValidator:
        return PhenotypicAbnormalityValidator(toy_hpo)

    def test_ok_input_produces_no_errors(self, validator: PhenotypicAbnormalityValidator,
                                         example_terms: typing.Sequence[SimpleFeature]):
        results = validator.validate(example_terms)
        assert results.is_ok()

    @pytest.mark.parametrize('curie',
                             (
                                     "HP:0012823",  # Clinical modifier
                                     "HP:0003825",  # Variable expressivity
                                     "HP:0003621",  # Juvenile onset
                             )
                             )
    def test_presence_of_clinical_modifier_produces_error(self, curie,
                                                          validator: PhenotypicAbnormalityValidator,
                                                          toy_hpo: hpotk.MinimalOntology,
                                                          example_terms: typing.Sequence[SimpleFeature]):
        example_terms = list(example_terms)
        example_terms.append(SimpleFeature(curie, True))
        results = validator.validate(example_terms)

        assert not results.is_ok()
        assert results.results[0] == ValidationResult(level=ValidationLevel.WARNING,
                                                      category='phenotypic_abnormality_descendant',
                                                      message=f'{toy_hpo.get_term(curie).name} '
                                                              f'[{toy_hpo.get_term(curie).identifier.value}] '
                                                              f'is not a descendant of '
                                                              'Phenotypic abnormality [HP:0000118]')


class TestObsoleteTermIdsValidator(TestBaseRuleValidator):

    @pytest.fixture
    def validator(self, toy_hpo: hpotk.MinimalOntology) -> ObsoleteTermIdsValidator:
        return ObsoleteTermIdsValidator(toy_hpo)

    def test_ok_input_produces_no_errors(self, validator: ObsoleteTermIdsValidator,
                                         example_terms: typing.Sequence[SimpleFeature]):
        results = validator.validate(example_terms)

        assert results.is_ok()

    def test_presence_of_an_obsolete_term_produces_error(self, validator: ObsoleteTermIdsValidator,
                                                         toy_hpo: hpotk.MinimalOntology,
                                                         example_terms: typing.Sequence[SimpleFeature]):
        curie = 'HP:0006010'  # obsolete Long fingers
        example_terms = list(example_terms)
        example_terms.append(SimpleFeature(curie, True))
        results = validator.validate(example_terms)

        assert not results.is_ok()
        assert results.results[0] == ValidationResult(level=ValidationLevel.WARNING,
                                                      category='obsolete_term_id_is_used',
                                                      message=f'Using the obsolete {curie} instead of '
                                                              f'{toy_hpo.get_term(curie).identifier.value} '
                                                              f'for {toy_hpo.get_term(curie).name}')
