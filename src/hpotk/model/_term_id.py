import abc


class TermId(metaclass=abc.ABCMeta):
    """
    A class for representing an ontology concept.

    The `TermId` has a natural ordering which compares two IDs first based on prefix and then value.
    Both comparisons are lexicographic.
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

    @staticmethod
    def _calculate_hash(prefix: str, id: str) -> int:
        """
        Calculate hash of a term ID from the members.
        :param prefix: the prefix part of the term ID (e.g. `HP` for `HP:1234567`) as a `str.
        :param id: the id part of the term ID (e.g. `1234567` for `HP:1234567`) as a str.
        :return: a hash as an `int`.
        """
        return hash((prefix, id))

    def __hash__(self) -> int:
        return self._calculate_hash(self.prefix, self.id)

    def __eq__(self, other):
        return isinstance(other, TermId) \
            and self.prefix == other.prefix \
            and self.id == other.id

    def __lt__(self, other):
        if isinstance(other, TermId):
            if self.prefix == other.prefix:
                return self.id < other.id
            else:
                return self.prefix < other.prefix
        else:
            return NotImplemented

    def __str__(self):
        return self.value


class DefaultTermId(TermId):
    """
    A default implementation of :class:`TermId` that stores the index of the delimiter and the value as a string
    and caches the hash value.
    """

    def __init__(self, value: str, idx: int):
        self._value = value
        self._idx = idx
        self._hash = self._calculate_hash(prefix=value[:idx], id=value[idx + 1:])

    @property
    def prefix(self) -> str:
        return self._value[:self._idx]

    @property
    def id(self) -> str:
        return self._value[self._idx + 1:]

    def __repr__(self):
        return f'DefaultTermId(idx={self._idx}, value={self._value})'

    def __hash__(self) -> int:
        return self._hash

    # TODO - make specific HPO TermId


class SimpleTermId(TermId):
    """
    The simplest possible implementation of a `TermId` that stores the entire curie and the position
    of the delimiter that separates the prefix and the id.
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

    def __repr__(self):
        return f'SimpleTermId(idx={self._idx}, value={self._value})'
