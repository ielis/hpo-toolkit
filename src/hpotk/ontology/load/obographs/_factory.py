import abc
import logging
import re
import typing

from hpotk.model import TermId, Term, MinimalTerm, Synonym, SynonymType, SynonymCategory, Definition
from ._model import Node, Meta, SynonymPropertyValue

logger = logging.getLogger(__name__)

MINIMAL_TERM = typing.TypeVar('MINIMAL_TERM', bound=MinimalTerm)

OBO_PURL_PT = re.compile(r'^http://purl\.obolibrary\.org/obo/(?P<value>.+)$')
HP_VAL_PT = re.compile(r'^hp(.*)#(?P<value>.+)$')
ORCID_PT = re.compile(r'.*orcid\.org/(?P<orcid>\d{4}-\d{4}-\d{4}-\d{4})$')


def create_alt_term_ids(node: Node) -> typing.List[TermId]:
    alt_term_ids = []
    if node.meta:
        for bpv in node.meta.basic_property_values:
            if bpv.pred is not None \
                    and bpv.val is not None \
                    and bpv.pred.endswith('#hasAlternativeId'):
                alt_term_ids.append(TermId.from_curie(bpv.val))
    return alt_term_ids


def create_synonyms(meta: Meta) -> typing.Optional[typing.List[Synonym]]:
    if len(meta.synonyms) == 0:
        return None
    else:
        return [parse_synonym(s) for s in meta.synonyms]


def parse_synonym(spv: SynonymPropertyValue) -> Synonym:
    synonym_category: typing.Optional[SynonymCategory] = parse_synonym_category(spv.pred)
    synonym_type: typing.Optional[SynonymType] = parse_synonym_type(spv.synonym_type)
    if len(spv.xrefs) != 0:
        xrefs = []
        for xref in spv.xrefs:
            parsed = parse_synonym_xref(xref)
            if parsed is not None:
                xrefs.append(parsed)
        xrefs = list(xrefs) if len(xrefs) != 0 else None  # shrink to fit
    else:
        xrefs = None

    return Synonym(name=spv.val, synonym_category=synonym_category, synonym_type=synonym_type, xrefs=xrefs)


def parse_synonym_category(synonym_category: str) -> typing.Optional[SynonymCategory]:
    if synonym_category == 'hasRelatedSynonym':
        return SynonymCategory.RELATED
    elif synonym_category == 'hasExactSynonym':
        return SynonymCategory.EXACT
    elif synonym_category == 'hasBroadSynonym':
        return SynonymCategory.BROAD
    elif synonym_category == 'hasNarrowSynonym':
        return SynonymCategory.NARROW
    else:
        logger.debug(f"Unknown synonym category {synonym_category}")
        return None


def parse_synonym_type(synonym_type: str) -> typing.Optional[SynonymType]:
    if synonym_type is None or len(synonym_type) == 0:
        return None
    hp_obo_matcher = OBO_PURL_PT.match(synonym_type)
    if hp_obo_matcher:
        value = hp_obo_matcher.group('value')
        hp_matcher = HP_VAL_PT.match(value)
        if hp_matcher:
            value = hp_matcher.group('value')
            if value in ('layperson', 'layperson term'):
                return SynonymType.LAYPERSON_TERM
            elif value == 'abbreviation':
                return SynonymType.ABBREVIATION
            elif value == 'uk_spelling':
                return SynonymType.UK_SPELLING
            elif value == 'obsolete_synonym':
                return SynonymType.OBSOLETE_SYNONYM
            elif value == 'plural_form':
                return SynonymType.PLURAL_FORM
        else:
            if value in ('HP_0034334', 'allelic_requirement'):
                return SynonymType.ALLELIC_REQUIREMENT

    logger.debug(f"Unknown synonym type {synonym_type}")
    return None


def parse_synonym_xref(xref) -> typing.Optional[TermId]:
    orcid_matcher = ORCID_PT.match(xref)
    if orcid_matcher:
        return TermId.from_curie(f'ORCID:{orcid_matcher.group("orcid")}')
    else:
        try:
            # TODO: this can contain many things. Investigate..
            return TermId.from_curie(xref)
        except ValueError:
            logger.debug(f'Unable to create a synonym xref from {xref}')
            return None


def create_xrefs(meta: Meta) -> typing.Optional[typing.List[TermId]]:
    if len(meta.xrefs) == 0:
        return None
    else:
        # TODO: Expecting that all xrefs are CURIES may be a bit too naive. Investigate..
        return [TermId.from_curie(xref.val) for xref in meta.xrefs]


class ObographsTermFactory(typing.Generic[MINIMAL_TERM], metaclass=abc.ABCMeta):
    """
    Term factory turns `TermId` and obographs `Node` into an ontology term.
    """

    @abc.abstractmethod
    def create_term(self, term_id: TermId, node: Node) -> typing.Optional[MINIMAL_TERM]:
        """
        Create `MinimalTerm` or a more specific instance for `TermId` and `Node`

        The term may not be created at the discretion of the factory, in which case `None` is returned.
        """
        pass


class MinimalTermFactory(ObographsTermFactory[MinimalTerm]):

    def create_term(self, term_id: TermId, node: Node) -> typing.Optional[MinimalTerm]:
        is_obsolete = node.meta is not None and node.meta.is_deprecated
        alt_term_ids = create_alt_term_ids(node)
        return MinimalTerm.create_minimal_term(term_id, node.lbl, alt_term_ids, is_obsolete)


class TermFactory(ObographsTermFactory[Term]):

    def create_term(self, term_id: TermId, node: Node) -> typing.Optional[Term]:
        if node.meta:
            if node.meta.definition is not None:
                d = node.meta.definition.val
                xrefs = node.meta.definition.xrefs
                definition = Definition(d, xrefs)
            else:
                definition = None
            comment = ', '.join(node.meta.comments) if len(node.meta.comments) > 0 else None
            alt_term_ids = create_alt_term_ids(node)
            synonyms = create_synonyms(node.meta)
            xrefs = create_xrefs(node.meta)

            return Term.create_term(term_id, name=node.lbl, alt_term_ids=alt_term_ids,
                                    is_obsolete=node.meta.is_deprecated, definition=definition, comment=comment,
                                    synonyms=synonyms, xrefs=xrefs)
        else:
            return Term.create_term(term_id, name=node.lbl, alt_term_ids=[],
                                    is_obsolete=False, definition=None, comment=None,
                                    synonyms=None, xrefs=None)
