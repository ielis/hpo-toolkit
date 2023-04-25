import typing
import abc
import enum

from collections import namedtuple

from hpotk.model import Identified, TermId


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
    `RuleValidator` checks if a sequence of :class:`Identified` or :class:`TermId` instances meet
    the validation requirements.

    The validators can check each item individually or as a collection, for instance,
    to discover violation of the annotation propagation rule, etc.

    The issues are returned as :class:`ValidationResults`.
    """

    @abc.abstractmethod
    def validate(self, items: typing.Sequence[typing.Union[Identified, TermId]]) -> ValidationResults:
        pass

    @staticmethod
    def extract_term_id(item: typing.Union[Identified, TermId]) -> TermId:
        if isinstance(item, Identified):
            return item.identifier
        elif isinstance(item, TermId):
            return item
        else:
            raise ValueError(f'Item {item} of type {type(item)} is not a TermId nor extends Identified')


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
