import typing
import abc
import enum

from collections import namedtuple

from hpotk.model import Identified


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
    `RuleValidator` checks if a sequence of `Identified` items meet the validation requirements.
    The issues are returned as `ValidationResults`.
    """

    @abc.abstractmethod
    def validate(self, items: typing.Sequence[Identified]) -> ValidationResults:
        pass


class ValidationRunner:
    """
    The runner applies a sequence of `RuleValidator`s on items and returns the results as `ValidationResults`.
    """

    def __init__(self, validators: typing.Sequence[RuleValidator]):
        self._validators = validators

    def validate_all(self, items: typing.Sequence[Identified]) -> ValidationResults:
        overall = []
        for validator in self._validators:
            results = validator.validate(items)
            for result in results.results:
                overall.append(result)

        return ValidationResults(overall)
