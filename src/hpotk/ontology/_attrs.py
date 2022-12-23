import abc
import typing

from hpotk.model import TermId

ID = typing.TypeVar('ID', bound=TermId)


class Versioned(metaclass=abc.ABCMeta):
    """
    Base class for entities that may have version.
    """

    @property
    @abc.abstractmethod
    def version(self) -> typing.Optional[str]:
        """
        :return: version `str` or `None` if the version is not available.
        """
        pass
