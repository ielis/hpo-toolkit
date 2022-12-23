import abc
import typing

from hpotk.model import TermId, Term, MinimalTerm

from ._model import Node

MINIMAL_TERM = typing.TypeVar('MINIMAL_TERM', bound=MinimalTerm)


def create_alt_term_ids(node: Node) -> typing.List[TermId]:
    alt_term_ids = []
    if node.meta:
        for bpv in node.meta.basic_property_values:
            if bpv.pred is not None \
                    and bpv.val is not None \
                    and bpv.pred.endswith('#hasAlternativeId'):
                alt_term_ids.append(TermId.from_curie(bpv.val))
    return alt_term_ids


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
            definition = node.meta.definition.val if node.meta.definition else None
            comment = ', '.join(node.meta.comments) if len(node.meta.comments) > 0 else None
            alt_term_ids = create_alt_term_ids(node)

            return Term.create_term(term_id, name=node.lbl, alt_term_ids=alt_term_ids,
                                    is_obsolete=node.meta.is_deprecated, definition=definition, comment=comment)
        else:
            return Term.create_term(term_id, name=node.lbl, alt_term_ids=[], is_obsolete=False, definition=None,
                                    comment=None)
