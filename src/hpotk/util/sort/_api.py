import abc
import typing

from hpotk.model import TermId, Identified


class TermIdSorting(metaclass=abc.ABCMeta):
    """
    `TermIdSorting` computes indices for sorting a sequence of identifiers/identified items.
    """

    @abc.abstractmethod
    def argsort(self, term_ids: typing.Sequence[typing.Union[TermId, Identified]]) -> typing.Sequence[int]:
        """
        Prepare indices for sorting a sequence of term IDs.

        :param term_ids: a sequence of term IDs or identified entities to sort.
        :return: a sequence of indices for sorting of the `term_ids` sequence.
        """
        pass
