import abc


class TermId(metaclass=abc.ABCMeta):
    """
    A class for representing ontology concept.
    """

    @staticmethod
    def from_curie(curie: str):
        """
        Create a `TermId` from a `str` where *prefix* and *id* are delimited either by a colon `:` (e.g. `HP:1234567`)
        or an underscore '_' (e.g. `NCIT_C3117`).
        :param curie: CURIE to be parsed
        :return: the created `TermId`
        :raises: ValueError if the value is mis-formatted.
        """
        if curie is None:
            raise ValueError(f'Curie must not be None')
        try:
            idx = curie.index(':')
        except ValueError:
            try:
                idx = curie.index('_')
            except ValueError:
                raise ValueError(f'The CURIE {curie} has no colon `:` or underscore `_`')

        return DefaultTermId(idx=idx, value=curie)

    @property
    @abc.abstractmethod
    def prefix(self) -> str:
        """
        Get `prefix` of the ontology concept. For instance, `HP` for `HP:1234567`.
        :return: the prefix `str`
        """
        pass

    @property
    @abc.abstractmethod
    def id(self) -> str:
        """
        Get `id` of the ontology concept. For instance, `1234567` for `HP:1234567`.
        :return: the id `str`
        """
        pass

    @property
    def value(self) -> str:
        """
        Get concept value consisting of `self.prefix` and `self.value`. For instance, `HP:1234567`.
        :return: concept value `str`
        """
        return self.prefix + ':' + self.id

    def __hash__(self) -> int:
        return hash((self.prefix, self.id))

    def __eq__(self, other):
        return isinstance(other, TermId) \
            and self.prefix == other.prefix \
            and self.id == other.id

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'TermId(prefix="{self.prefix}", id="{self.id}")'


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


class DefaultTermId(TermId):
    """
    A default implementation of :class:`TermId` that stores the index of the delimiter and the value as a string.
    """

    def __init__(self, value: str, idx: int):
        self._value = value
        self._idx = idx

    @property
    def prefix(self) -> str:
        return self._value[:self._idx]

    @property
    def id(self) -> str:
        return self._value[self._idx + 1:]

# TODO - make specific HPO TermId
