import hpotk
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
    def create_minimal_term(term_id: typing.Union[TermId, str],
                            name: str,
                            alt_term_ids: typing.Iterable[typing.Union[TermId, str]],
                            is_obsolete: bool):
        """
        Create a `MinimalTerm` from its components.

        :param term_id: a `TermId` or a CURIE `str` (e.g. 'HP:0001250').
        :param name: term name (e.g. Seizure) .
        :param alt_term_ids: an iterable with `TermId`s that represent the alternative IDs of the term.
        :param is_obsolete: `True` if the `MinimalTerm` has been obsoleted, or `False` otherwise.
        :return:
        """
        return DefaultMinimalTerm(term_id, name, alt_term_ids, is_obsolete)

    @property
    @abc.abstractmethod
    def alt_term_ids(self) -> typing.Sequence[TermId]:
        """
        Get a sequence of identifiers of `Term`s that have been obsolete and replaced by this `Term`.

        :return: a sequence of identifiers.
        """
        pass

    @property
    def is_current(self) -> bool:
        """
        Test if the term is current (*not* obsolete).

        :return: `True` if the term is current and `False` otherwise.
        """
        return not self.is_obsolete

    @property
    @abc.abstractmethod
    def is_obsolete(self) -> bool:
        """
        Test if the term is obsolete (*not* current).

        :return: `True` if the term is obsolete and `False` otherwise.
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

    def is_obsolete(self) -> bool:
        return self == SynonymType.OBSOLETE_SYNONYM

    def is_current(self) -> bool:
        return not self.is_obsolete()


class Synonym(Named):

    def __init__(self, name: str,
                 synonym_category: typing.Optional[SynonymCategory] = None,
                 synonym_type: typing.Optional[SynonymType] = None,
                 xrefs: typing.Optional[typing.Sequence[TermId]] = None):
        self._name = name
        self._scat = synonym_category
        self._stype = synonym_type
        self._xrefs = xrefs

    @property
    def name(self) -> str:
        return self._name

    @property
    def category(self) -> typing.Optional[SynonymCategory]:
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
    def xrefs(self) -> typing.Optional[typing.Sequence[TermId]]:
        return self._xrefs

    def __eq__(self, other):
        isinstance(other, Synonym) \
        and self.name == other.name \
        and self.category == other.category \
        and self.synonym_type == other.synonym_type \
        and self.xrefs == other.xrefs

    def __str__(self):
        return f'Synonym(' \
               f'name="{self.name}", ' \
               f'category={self.category}, ' \
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
    def create_term(identifier: typing.Union[TermId, str],
                    name: str,
                    alt_term_ids: typing.Iterable[typing.Union[TermId, str]],
                    is_obsolete: bool,
                    definition: typing.Optional[str],
                    comment: typing.Optional[str],
                    synonyms: typing.Optional[typing.Sequence[Synonym]],
                    xrefs: typing.Optional[typing.Sequence[TermId]]):
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
        Get the term's comment string.

        :return: the term's comment string.
        """
        pass

    @property
    @abc.abstractmethod
    def synonyms(self) -> typing.Optional[typing.Sequence[Synonym]]:
        """
        Get all synonyms (including obsolete) of the term.

        :return: a sequence of synonyms or `None` if the term has no synonyms.
        """
        pass

    def current_synonyms(self) -> typing.Iterable[Synonym]:
        """
        Get an iterable with current synonyms of the term.

        :return: an iterable with current synonyms or an empty iterable if the term has no synonyms.
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
    def xrefs(self) -> typing.Optional[typing.Sequence[TermId]]:
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


def map_to_term_id(value: typing.Union[TermId, str]) -> TermId:
    if isinstance(value, TermId):
        return value
    elif isinstance(value, str):
        return TermId.from_curie(value)
    else:
        raise ValueError(f'Expected a `TermId` or `str` but got {type(value)}')


def validate_name(name: typing.Optional[str]) -> str:
    # Some obsolete nodes do not have labels in the Obographs format.
    # We assign an empty string.
    if name is None:
        return ''
    else:
        return hpotk.util.validate_instance(name, str, 'name')


class DefaultMinimalTerm(MinimalTerm):

    def __init__(self, identifier: typing.Union[TermId, str],
                 name: str,
                 alt_term_ids: typing.Iterable[typing.Union[TermId, str]],
                 is_obsolete: bool):
        self._id = hpotk.util.validate_instance(map_to_term_id(identifier), TermId, 'identifier')
        self._name = validate_name(name)
        self._alts = tuple(map(map_to_term_id, alt_term_ids))
        self._is_obsolete = hpotk.util.validate_instance(is_obsolete, bool, 'is_obsolete')

    @property
    def identifier(self) -> TermId:
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


def validate_synonyms(synonyms: typing.Optional[typing.Sequence[Synonym]]):
    if synonyms is None:
        return None
    else:
        validated = []
        for i, s in enumerate(synonyms):
            validated.append(hpotk.util.validate_instance(s, Synonym, f'synonym #{i}'))
        return tuple(validated)


class DefaultTerm(DefaultMinimalTerm, Term):

    def __init__(self, identifier: typing.Union[TermId, str],
                 name: str,
                 alt_term_ids: typing.Iterable[typing.Union[TermId, str]],
                 is_obsolete: bool,
                 definition: typing.Optional[str],
                 comment: typing.Optional[str],
                 synonyms: typing.Optional[typing.Sequence[Synonym]],
                 xrefs: typing.Optional[typing.Sequence[typing.Union[TermId, str]]]):
        DefaultMinimalTerm.__init__(self, identifier=identifier, name=name,
                                    alt_term_ids=alt_term_ids, is_obsolete=is_obsolete)
        self._definition = hpotk.util.validate_optional_instance(definition, str, 'definition')
        self._comment = hpotk.util.validate_optional_instance(comment, str, 'comment')
        self._synonyms = validate_synonyms(synonyms)
        self._xrefs = tuple(map(map_to_term_id, xrefs)) if xrefs is not None else None

    @property
    def definition(self) -> str:
        return self._definition

    @property
    def comment(self) -> str:
        return self._comment

    @property
    def synonyms(self) -> typing.Optional[typing.Sequence[Synonym]]:
        return self._synonyms

    @property
    def xrefs(self) -> typing.Optional[typing.Sequence[TermId]]:
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
               f'alt_term_ids="{self._alts}")'
