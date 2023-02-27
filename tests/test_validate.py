import os
import unittest

from pkg_resources import resource_filename

from hpotk.model import MinimalTerm, TermId
from hpotk.ontology.load.obographs import load_minimal_ontology
from hpotk.validate import ValidationResult, ValidationLevel
from hpotk.validate import AnnotationPropagationValidator, PhenotypicAbnormalityValidator


TOY_HPO = resource_filename(__name__, os.path.join('data', 'hp.toy.json'))


class TestBaseRuleValidator(unittest.TestCase):

    o = None
    example_terms = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.o = load_minimal_ontology(TOY_HPO)
        cls.example_terms = [
            MinimalTerm.create_minimal_term(
                TermId.from_curie('HP:0001166'),
                name='Arachnodactyly', alt_term_ids=[], is_obsolete=False),
            MinimalTerm.create_minimal_term(
                TermId.from_curie('HP:0002266'),
                name='Focal clonic seizure', alt_term_ids=[], is_obsolete=False),
            MinimalTerm.create_minimal_term(
                TermId.from_curie('HP:0032648'),
                name='Tubularization of Bowman capsule', alt_term_ids=[], is_obsolete=False)
        ]


class TestAnnotationPropagationValidator(TestBaseRuleValidator):

    def setUp(self) -> None:
        self.validator = AnnotationPropagationValidator(self.o)

    def test_empty_input_is_allowed(self):
        results = self.validator.validate([])
        self.assertTrue(results.is_ok())

    def test_ok_input_produces_no_errors(self):
        results = self.validator.validate(self.example_terms)
        self.assertTrue(results.is_ok())

    def test_ancestor_presence_produces_error(self):
        example_terms = list(self.example_terms)
        example_terms.append(
            MinimalTerm.create_minimal_term(
                TermId.from_curie('HP:0100807'), name='Long fingers', alt_term_ids=[], is_obsolete=False)
        )
        results = self.validator.validate(example_terms)
        self.assertFalse(results.is_ok())
        self.assertEqual(results.results[0],
                         ValidationResult(level=ValidationLevel.ERROR, category='annotation_propagation',
                                          message='Terms should not contain both Arachnodactyly [HP:0001166] '
                                                  'and its ancestor Long fingers[HP:0100807]'))


class TestPhenotypicAbnormalityValidator(TestBaseRuleValidator):

    def setUp(self) -> None:
        self.validator = PhenotypicAbnormalityValidator(self.o)

    def test_ok_input_produces_no_errors(self):
        results = self.validator.validate(self.example_terms)
        self.assertTrue(results.is_ok())

    # def test_clinical_modifier_presence_produces_error(self):
    #     example_terms = list(self.example_terms)
    #     example_terms.append(
    #         MinimalTerm.create_minimal_term(
    #             TermId.from_curie('HP:0012823'), name='Clinical modifier', alt_term_ids=[], is_obsolete=False)
    #     )
    #     results = self.validator.validate(example_terms)
    #     self.assertFalse(results.is_ok())
    #     print(results)
    #
        pass
