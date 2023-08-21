import os
import unittest

import ddt
from pkg_resources import resource_filename

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


class TestBaseRuleValidator(unittest.TestCase):

    o = None
    example_terms = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.o = load_minimal_ontology(TOY_HPO)
        cls.example_terms = [
            SimpleFeature('HP:0001166', True),  # Arachnodactyly
            SimpleFeature('HP:0001250', True),  # Seizure
            SimpleFeature('HP:0032648', True),  # Tubularization of Bowman capsule
            SimpleFeature('HP:0000805', False)  # excluded Enuresis
        ]


@ddt.ddt
class TestAnnotationPropagationValidator(TestBaseRuleValidator):

    def setUp(self) -> None:
        self.validator = AnnotationPropagationValidator(self.o)

    def test_empty_input_is_allowed(self):
        results = self.validator.validate([])
        self.assertTrue(results.is_ok())

    def test_ok_input_produces_no_errors(self):
        results = self.validator.validate(self.example_terms)
        self.assertTrue(results.is_ok())

    def test_obsolete_ancestor_produces_error(self):
        example_terms = list(self.example_terms)
        example_terms.append(TermId.from_curie('HP:0006010'))

        results = self.validator.validate(example_terms)

        self.assertFalse(results.is_ok())
        self.assertEqual(results.results[0],
                         ValidationResult(level=ValidationLevel.ERROR, category='annotation_propagation',
                                          message='Terms should not contain both present Arachnodactyly [HP:0001166] '
                                                  f'and its present or excluded ancestor Long fingers [HP:0100807]'))

    @ddt.data(
        ("HP:0100807", True, 'HP:0001166', True),   # present Long fingers vs. present Arachnodactyly
        ("HP:0100807", False, 'HP:0001166', True),  # excluded Long fingers vs. present Arachnodactyly

        # The case is commented out since it is possible to have some abnormality but excluded specific abnormality
        # ("HP:0000014", True, 'HP:0000805', False),  # present Abnormality of the bladder vs. excluded Enuresis

        ("HP:0000014", False, 'HP:0000805', False),  # excluded Abnormality of the bladder vs. excluded Enuresis
    )
    @ddt.unpack
    def test_ancestor_presence_produces_error(self, ancestor_curie, ancestor_status, base_curie, base_status):
        example_terms = list(self.example_terms)
        example_terms.append(SimpleFeature(ancestor_curie, ancestor_status))

        results = self.validator.validate(example_terms)

        self.assertFalse(results.is_ok())
        self.assertEqual(1, len(results.results))
        first = results.results[0]
        self.assertEqual(ValidationLevel.ERROR, first.level)
        self.assertEqual('annotation_propagation', first.category)

        state = 'present' if base_status else 'excluded'
        self.assertEqual(f'Terms should not contain both {state} '
                         f'{self.o.get_term(base_curie).name} [{self.o.get_term(base_curie).identifier.value}] '
                         f'and its present or excluded ancestor '
                         f'{self.o.get_term(ancestor_curie).name} [{ancestor_curie}]',
                         first.message)


@ddt.ddt
class TestPhenotypicAbnormalityValidator(TestBaseRuleValidator):

    def setUp(self) -> None:
        self.validator = PhenotypicAbnormalityValidator(self.o)

    def test_ok_input_produces_no_errors(self):
        results = self.validator.validate(self.example_terms)
        self.assertTrue(results.is_ok())

    @ddt.data(
        ("HP:0012823",),  # Clinical modifier
        ("HP:0003825",),  # Variable expressivity
        ("HP:0003621",),  # Juvenile onset
    )
    @ddt.unpack
    def test_presence_of_clinical_modifier_produces_error(self, curie):
        example_terms = list(self.example_terms)
        example_terms.append(SimpleFeature(curie, True))
        results = self.validator.validate(example_terms)
        self.assertFalse(results.is_ok())
        self.assertEqual(results.results[0],
                         ValidationResult(level=ValidationLevel.WARNING, category='phenotypic_abnormality_descendant',
                                          message=f'{self.o.get_term(curie).name} [{self.o.get_term(curie).identifier.value}] is not a descendant of '
                                                  'Phenotypic abnormality [HP:0000118]'))


@ddt.ddt
class TestObsoleteTermIdsValidator(TestBaseRuleValidator):

    def setUp(self) -> None:
        self.validator = ObsoleteTermIdsValidator(self.o)

    def test_ok_input_produces_no_errors(self):
        results = self.validator.validate(self.example_terms)
        self.assertTrue(results.is_ok())

    def test_presence_of_an_obsolete_term_produces_error(self):
        curie = 'HP:0006010'  # obsolete Long fingers
        example_terms = list(self.example_terms)
        example_terms.append(SimpleFeature(curie, True))
        results = self.validator.validate(example_terms)
        self.assertFalse(results.is_ok())
        self.assertEqual(results.results[0],
                         ValidationResult(level=ValidationLevel.WARNING, category='obsolete_term_id_is_used',
                                          message=f'Using the obsolete {curie} instead of '
                                                  f'{self.o.get_term(curie).identifier.value} '
                                                  f'for {self.o.get_term(curie).name}'))
