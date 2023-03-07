import abc
import typing

from hpotk.annotations import HpoDiseases


class HpoDiseaseLoader(metaclass=abc.ABCMeta):
    """
    Loader for reading data into :class:`HpoDiseases` container.
    """

    @abc.abstractmethod
    def load(self, file: typing.Union[typing.IO, str]) -> HpoDiseases:
        pass
