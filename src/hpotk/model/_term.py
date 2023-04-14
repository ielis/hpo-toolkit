import abc
import enum
import typing

from ._base import Identified, Named
from ._term_id import TermId


class MinimalTerm(Identified, Named, metaclass=abc.ABCMeta):
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
    def alt_term_ids(self) -> typing.Sequence[TermId]:
        """
        :return: a sequence of identifiers of `Term`s that have been obsolete and replaced by this `Term`.
        """
        pass

    @property
    def is_current(self) -> bool:
        """
        :return: `True` if the term is current (*not* obsolete).
        """
        return not self.is_obsolete

    @property
    @abc.abstractmethod
    def is_obsolete(self) -> bool:
        """
        :return: `True` if the term has been obsolete.
        """
        pass

    def __eq__(self, other):
        return isinstance(other, MinimalTerm) \
            and self.identifier == other.identifier \
            and self.name == other.name \
            and self.alt_term_ids == other.alt_term_ids \
            and self.is_obsolete == other.is_obsolete

    def __str__(self):
        return f'MinimalTerm(' \
               f'identifier="{self.identifier}", ' \
               f'name="{self.name}", ' \
               f'alt_term_ids={self.alt_term_ids}, ' \
               f'is_obsolete={self.is_obsolete})'


class SynonymCategory(enum.Enum):
    """
    Synonym category.
    """
    EXACT = enum.auto()
    RELATED = enum.auto()
    BROAD = enum.auto()
    NARROW = enum.auto()


class SynonymType(enum.Enum):
    """
    Synonym type, as provided by Obographs.
    """
    LAYPERSON_TERM = enum.auto()
    ABBREVIATION = enum.auto()
    UK_SPELLING = enum.auto()
    OBSOLETE_SYNONYM = enum.auto()
    PLURAL_FORM = enum.auto()
    ALLELIC_REQUIREMENT = enum.auto()

    # We may not need these, unless we support ECTO
    # IUPAC_NAME = enum.auto()
    # INN = enum.auto()
    # BRAND_NAME = enum.auto()
    # IN_PART = enum.auto()
    # SYNONYM = enum.auto()
    # BLAST_NAME = enum.auto()
    # GENBANK_COMMON_NAME = enum.auto()
    # COMMON_NAME = enum.auto()

    def is_obsolete(self):
        return self == SynonymType.OBSOLETE_SYNONYM

    def is_current(self):
        return not self.is_obsolete()


class Synonym(Named):

    def __init__(self, name: str,
                 synonym_category: typing.Optional[SynonymCategory],
                 synonym_type: typing.Optional[SynonymType],
                 xrefs: typing.Optional[typing.List[TermId]] = None):
        self._name = name
        self._scat = synonym_category
        self._stype = synonym_type
        self._xrefs = xrefs

    @property
    def name(self) -> str:
        return self._name

    @property
    def synonym_category(self) -> typing.Optional[SynonymCategory]:
        """
        :return: an instance of :class:`SynonymCategory` or ``None``.
        """
        return self._scat

    @property
    def synonym_type(self) -> typing.Optional[SynonymType]:
        """
        :return: an instance of :class:`SynonymType` or ``None``.
        """
        return self._stype

    @property
    def xrefs(self) -> typing.Optional[typing.List[TermId]]:
        return self._xrefs

    def __eq__(self, other):
        isinstance(other, Synonym) \
        and self.name == other.name \
        and self.synonym_category == other.synonym_category \
        and self.synonym_type == other.synonym_type \
        and self.xrefs == other.xrefs

    def __str__(self):
        return f'Synonym(' \
               f'name="{self.name}", ' \
               f'synonym_category={self.synonym_category}, ' \
               f'synonym_type={self.synonym_type}, ' \
               f'xrefs="{self.xrefs}")'

    def __repr__(self):
        return str(self)


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
                    comment: typing.Optional[str],
                    synonyms: typing.Optional[typing.List[Synonym]],
                    xrefs: typing.Optional[typing.List[TermId]]):
        return DefaultTerm(identifier, name, alt_term_ids, is_obsolete, definition, comment, synonyms, xrefs)

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

    @property
    @abc.abstractmethod
    def synonyms(self) -> typing.Optional[typing.List[Synonym]]:
        """
        :return: all synonyms (including obsolete) of the term.
        """
        pass

    def current_synonyms(self) -> typing.Iterable[Synonym]:
        """
        :return: iterable over current (non-obsolete) synonyms of the term.
        """
        return self._synonyms_iter(lambda synonym:
                                   synonym.synonym_type is None
                                   or synonym.synonym_type.is_current())

    def obsolete_synonyms(self) -> typing.Iterable[Synonym]:
        """
        :return: iterable over obsolete synonyms of the term.
        """
        return self._synonyms_iter(lambda synonym:
                                   synonym.synonym_type is not None
                                   and synonym.synonym_type.is_obsolete())

    def _synonyms_iter(self, filter_f):
        if self.synonyms is None:
            return ()
        else:
            for synonym in self.synonyms:
                if filter_f(synonym):
                    yield synonym

    @property
    @abc.abstractmethod
    def xrefs(self) -> typing.Optional[typing.List[TermId]]:
        """
        :return: term's cross-references
        """
        pass

    def __eq__(self, other):
        return MinimalTerm.__eq__(self, other) \
            and isinstance(other, Term) \
            and self.definition == other.definition \
            and self.comment == other.comment \
            and self.synonyms == other.synonyms \
            and self.xrefs == other.xrefs

    def __str__(self):
        return f'Term(' \
               f'identifier={self.identifier}, ' \
               f'name="{self.name}", ' \
               f'definition={self.definition}, ' \
               f'comment={self.comment}, ' \
               f'synonyms={self.synonyms}, ' \
               f'xrefs={self.xrefs}, ' \
               f'is_obsolete={self.is_obsolete}, ' \
               f'alt_term_ids="{self.alt_term_ids}")'


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

    def __repr__(self):
        return f'DefaultMinimalTerm(' \
               f'identifier={self._id},' \
               f' name="{self._name}",' \
               f' is_obsolete={self._is_obsolete},' \
               f' alt_term_ids="{self._alts}")'


class DefaultTerm(Term):

    def __init__(self, identifier: TermId,
                 name: str,
                 alt_term_ids: typing.Sequence[TermId],
                 is_obsolete: typing.Optional[bool],
                 definition: typing.Optional[str],
                 comment: typing.Optional[str],
                 synonyms: typing.Optional[typing.List[Synonym]],
                 xrefs: typing.Optional[typing.List[TermId]]):
        self._id = identifier
        self._name = name
        self._alt_term_ids = alt_term_ids
        self._is_obsolete = False if is_obsolete is None else is_obsolete
        self._definition = definition
        self._comment = comment
        self._synonyms = synonyms
        self._xrefs = xrefs

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

    @property
    def synonyms(self) -> typing.Optional[typing.List[Synonym]]:
        return self._synonyms

    @property
    def xrefs(self) -> typing.Optional[typing.List[TermId]]:
        return self._xrefs

    def __repr__(self):
        return f'DefaultTerm(' \
               f'identifier={self._id}, ' \
               f'name="{self._name}", ' \
               f'definition={self._definition}, ' \
               f'comment={self._comment}, ' \
               f'synonyms={self._synonyms}, ' \
               f'xrefs={self._xrefs}, ' \
               f'is_obsolete={self._is_obsolete}, ' \
               f'alt_term_ids="{self._alt_term_ids}")'
