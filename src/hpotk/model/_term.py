import abc
import typing

from ._term_id import Identified, TermId


class MinimalTerm(Identified, metaclass=abc.ABCMeta):
    """
    Minimal information regarding an ontology concept.

    `MinimalTerm` has an `identifier`, a `name`, a sequence of alternate IDs (IDs of obsolete terms that should be
    replaced by this term), and obsoletion status.
    """

    @staticmethod
    def create_minimal_term(term_id: TermId,
                            name: str,
                            alt_term_ids: typing.Sequence[TermId],
                            is_obsolete: bool):
        return DefaultMinimalTerm(term_id, name, alt_term_ids, is_obsolete)

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """
        :return: the human-readable name of the term.
        """
        pass

    @property
    @abc.abstractmethod
    def alt_term_ids(self) -> typing.Sequence[TermId]:
        """
        :return: a sequence of identifiers of `Term`s that have been obsoleted and replaced by this `Term`.
        """
        pass

    @property
    def is_current(self) -> bool:
        """
        :return: `True` if the term is current (*not* obsoleted).
        """
        return not self.is_obsolete

    @property
    @abc.abstractmethod
    def is_obsolete(self) -> bool:
        """
        :return: `True` if the term has been obsoleted.
        """
        pass

    def __eq__(self, other):
        return isinstance(other, MinimalTerm) \
            and self.identifier == other.identifier \
            and self.name == other.name \
            and self.alt_term_ids == other.alt_term_ids \
            and self.is_obsolete == other.is_obsolete

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'MinimalTerm(identifier="{self.identifier}", name="{self.name}")'


class Term(MinimalTerm, metaclass=abc.ABCMeta):
    """
    A representation of an ontology concept.
    """

    # TODO - add the remaining attributes from phenol's Term?

    @staticmethod
    def create_term(identifier: TermId,
                    name: str,
                    alt_term_ids: typing.Sequence[TermId],
                    is_obsolete: typing.Optional[bool],
                    definition: typing.Optional[str],
                    comment: typing.Optional[str]):
        return DefaultTerm(identifier, name, alt_term_ids, is_obsolete, definition, comment)

    @property
    @abc.abstractmethod
    def definition(self) -> typing.Optional[str]:
        """
        :return: the term's definition.
        """
        pass

    @property
    @abc.abstractmethod
    def comment(self) -> str:
        """
        :return: the term's comment string.
        """
        pass

    # TODO - add Xrefs and dbXrefs

    def __eq__(self, other):
        return MinimalTerm.__eq__(self, other) \
            and isinstance(other, Term) \
            and self.definition == other.definition \
            and self.comment == other.comment

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'Term(identifier={self.identifier}, name="{self.name}", definition={self.definition}, comment={self.comment}, is_obsolete={self.is_obsolete}, alt_term_ids="{self.alt_term_ids}")'


class DefaultMinimalTerm(MinimalTerm):

    def __init__(self, identifier: TermId,
                 name: str,
                 alt_term_ids: typing.Sequence[TermId],
                 is_obsolete: bool):
        self._id = identifier
        self._name = name
        self._alts = alt_term_ids
        self._is_obsolete = is_obsolete

    @property
    def identifier(self):
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def alt_term_ids(self) -> typing.Sequence[TermId]:
        return self._alts

    @property
    def is_obsolete(self) -> bool:
        return self._is_obsolete


class DefaultTerm(Term):

    def __init__(self, identifier: TermId,
                 name: str,
                 alt_term_ids: typing.Sequence[TermId],
                 is_obsolete: typing.Optional[bool],
                 definition: typing.Optional[str],
                 comment: typing.Optional[str]):
        self._id = identifier
        self._name = name
        self._alt_term_ids = alt_term_ids
        self._is_obsolete = False if is_obsolete is None else is_obsolete
        self._definition = definition
        self._comment = comment

    @property
    def identifier(self) -> TermId:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def alt_term_ids(self) -> typing.Sequence[TermId]:
        return self._alt_term_ids

    @property
    def is_obsolete(self) -> bool:
        return self._is_obsolete

    @property
    def definition(self) -> str:
        return self._definition

    @property
    def comment(self) -> str:
        return self._comment
