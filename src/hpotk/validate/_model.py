import typing
import abc
import enum

from collections import namedtuple

from hpotk.model import Identified, TermId
from ._util import SimpleFeature, map_to_stateful_feature


class ValidationLevel(enum.Enum):
    WARNING = 1
    ERROR = 2


ValidationResult = namedtuple('ValidationResult', field_names=['level', 'category', 'message'])


class ValidationResults:
    """
    Results of a single validation.
    """

    def __init__(self, results: typing.Sequence[ValidationResult]):
        self._results = results
        
    @property
    def results(self) -> typing.Sequence[ValidationResult]:
        return self._results

    def is_ok(self) -> bool:
        return len(self._results) == 0

    def __str__(self):
        return f"ValidationResults(is_ok={self.is_ok()}, n_results={len(self._results)})"

    def __repr__(self) -> str:
        return f"ValidationResults(results={[self._results]})"


class RuleValidator(metaclass=abc.ABCMeta):
    """
    `RuleValidator` checks if a sequence of :class:`Identified` or :class:`TermId` items meet
    the validation requirements. The observation status is included in case the items extend :class:`ObservableFeature`.

    The validators can check each item individually or as a collection, for instance,
    to discover violation of the annotation propagation rule, etc.

    The issues are returned as :class:`ValidationResults`.
    """

    @abc.abstractmethod
    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        pass

    @staticmethod
    def _extract_stateful_feature(item: typing.Union[Identified, TermId]) -> SimpleFeature:
        return map_to_stateful_feature(item)


class ValidationRunner:
    """
    The runner applies a sequence of `RuleValidator`s on items and returns the results as `ValidationResults`.
    """

    def __init__(self, validators: typing.Sequence[RuleValidator]):
        self._validators = validators

    def validate_all(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        overall = []
        for validator in self._validators:
            results = validator.validate(items)
            for result in results.results:
                overall.append(result)

        return ValidationResults(overall)
