import abc

from ._term_id import TermId


class Identified(metaclass=abc.ABCMeta):
    """
    An entity that has a CURIE identifier.
    """

    @property
    @abc.abstractmethod
    def identifier(self) -> TermId:
        """
        :return: the identifier of the entity.
        """
        pass


class Named(metaclass=abc.ABCMeta):
    """
    An entity that has human-readable name or label.
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        :return: the human-readable name of the entity
        """
        pass
