import typing
import abc
import enum

from collections import namedtuple

from hpotk.model import Identified, TermId
from ._util import SimpleFeature, map_to_stateful_feature


class ValidationLevel(enum.Enum):
    """
    An enumeration of the validation levels.
    """

    WARNING = 1
    """
    Validation warning represents a potential issue that can be fixed. 
    """

    ERROR = 2
    """
    Validation error represents an issue that MUST be fixed
    """


ValidationResult = namedtuple('ValidationResult', field_names=['level', 'category', 'message'])
"""
A tuple of :class:`ValidationLevel`, a validation `category` string, and human-centric `message`. 
"""


class ValidationResults:
    """
    A container for results of a single validation run.

    :param results:
    """

    def __init__(self, results: typing.Sequence[ValidationResult]):
        self._results = results
        
    @property
    def results(self) -> typing.Sequence[ValidationResult]:
        """
        Get a sequence of validation results.
        """
        return self._results

    def is_ok(self) -> bool:
        """
        Test if the validation run found no errors.

        :return: `True` if no errors were found or `False` otherwise.
        """
        return len(self._results) == 0

    def __str__(self):
        return f"ValidationResults(is_ok={self.is_ok()}, n_results={len(self._results)})"

    def __repr__(self) -> str:
        return f"ValidationResults(results={[self._results]})"


class RuleValidator(metaclass=abc.ABCMeta):
    """
    `RuleValidator` checks if a sequence of :class:`hpotk.model.Identified` or :class:`hpotk.model.TermId` items meet
    the validation requirements.
    The observation status is included in case the items extend :class:`hpotk.model.ObservableFeature`.

    The validators can check each item individually or as a collection, for instance,
    to discover violation of the annotation propagation rule, etc.

    The issues are returned as :class:`ValidationResults`.
    """

    @abc.abstractmethod
    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        """
        Validate the sequence of term IDs or items that have an identifier.

        :param items: the items to validate.
        :return: results packaged in :class:`ValidationResults` container.
        """
        pass

    @staticmethod
    def _extract_stateful_feature(item: typing.Union[Identified, TermId]) -> SimpleFeature:
        return map_to_stateful_feature(item)


class ValidationRunner:
    """
    The runner applies a sequence of rule validators on items and packs the results
    into :class:`ValidationResults`.

    :param validators: a sequence of :class:`RuleValidator`\ s to apply.
    """

    def __init__(self, validators: typing.Sequence[RuleValidator]):
        self._validators = validators

    def validate_all(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        """
        Validate the `items` with all rules.

        :return: the results packed into :class:`ValidationResults`.
        """
        overall = []
        for validator in self._validators:
            results = validator.validate(items)
            for result in results.results:
                overall.append(result)

        return ValidationResults(overall)
