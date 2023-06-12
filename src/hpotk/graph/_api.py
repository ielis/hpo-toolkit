import abc
import typing

from hpotk.model import TermId, Identified

# TODO - enforce presence of the natural ordering?
# Note, the NODE must also have natural ordering.
NODE = typing.TypeVar('NODE', bound=TermId)
# Term ID that is added as an artificial root if >1 root candidates are found in the ontology graph.
OWL_THING = TermId.from_curie("owl:Thing")


class OntologyGraph(typing.Generic[NODE], metaclass=abc.ABCMeta):
    """
    A simple graph with one node type and one edge type.

    The graph is generic over a node type which must extend :class:`TermId`.
    The graph must not be empty, it must consist of at least one node.
    """

    @property
    @abc.abstractmethod
    def root(self) -> NODE:
        """
        Get the root node of the ontology graph.
        """
        pass

    @abc.abstractmethod
    def get_children(self, source: typing.Union[str, NODE, Identified],
                     include_source: bool = False) -> typing.Iterable[NODE]:
        """
        Get an iterable with the children of the `source` node.

        :param source: a :class:`TermId`, an item that *has* a :class:`TermId` (:class:`Identified`), or a curie `str`
        representing the source node.
        :param include_source: `True` if the `source` should be included among the children, `False` otherwise. 
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_descendants(self, source: typing.Union[str, NODE, Identified],
                        include_source: bool = False) -> typing.Iterable[NODE]:
        """
        Get an iterable with the descendants of the `source` node.

        :param source: a :class:`TermId`, an item that *has* a :class:`TermId` (:class:`Identified`), or a curie `str`
        representing the source node.
        :param include_source: `True` if the `source` should be included among the descendants, `False` otherwise.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_parents(self, source: typing.Union[str, NODE, Identified],
                    include_source: bool = False) -> typing.Iterable[NODE]:
        """
        Get an iterable with the parents of the `source` node.

        :param source: a :class:`TermId`, an item that *has* a :class:`TermId` (:class:`Identified`), or a curie `str`
        representing the source node.
        :param include_source: `True` if the `source` should be included among the parents, `False` otherwise.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_ancestors(self, source: typing.Union[str, NODE, Identified],
                      include_source: bool = False) -> typing.Iterable[NODE]:
        """
        Get an iterable with the ancestors of the `source` node.

        :param source: a :class:`TermId`, an item that *has* a :class:`TermId` (:class:`Identified`), or a curie `str`
        representing the source node.
        :param include_source: `True` if the `source` should be included among the ancestors, `False` otherwise.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    def is_leaf(self, node: typing.Union[str, NODE, Identified]) -> bool:
        """
        Return `True` if the `node` is a leaf node - a node with no descendants.
        :raises ValueError: if `node` is not present in the graph.
        """
        for _ in self.get_descendants(node):
            return False
        return True

    def is_parent_of(self, sub: typing.Union[str, NODE, Identified],
                     obj: typing.Union[str, NODE, Identified]) -> bool:
        """
        Return `True` if the subject `sub` is a parent of the object `obj`.

        :param sub: a graph node.
        :param obj: other graph node.
        :return: `True` if the `sub` is a parent of the `obj`.
        :raises ValueError: if `obj` is not present in the graph.
        """
        return self._run_query(self.get_parents, sub, obj)

    def is_ancestor_of(self, sub: typing.Union[str, NODE, Identified],
                       obj: typing.Union[str, NODE, Identified]) -> bool:
        """
        Return `True` if the subject `sub` is an ancestor of the object `obj`.

        :param sub: a graph node.
        :param obj: other graph node.
        :return: `True` if the `sub` is an ancestor of the `obj`.
        :raises ValueError: if `obj` is not present in the graph.
        """
        return self._run_query(self.get_ancestors, sub, obj)

    def is_child_of(self, sub: typing.Union[str, NODE, Identified],
                    obj: typing.Union[str, NODE, Identified]) -> bool:
        """
        Return `True` if the `sub` is a child of the `obj`.

        :param sub: a graph node.
        :param obj: other graph node.
        :return: `True` if the `sub` is a child of the `obj`.
        :raises ValueError: if `obj` is not present in the graph.
        """
        return self._run_query(self.get_children, sub, obj)

    def is_descendant_of(self, sub: typing.Union[str, NODE, Identified],
                         obj: typing.Union[str, NODE, Identified]) -> bool:
        """
        Return `True` if the `sub` is a descendant of the `obj`.

        :param sub: a graph node.
        :param obj: other graph node.
        :return: `True` if the `sub` is a descendant of the `obj`.
        :raises ValueError: if `obj` is not present in the graph.
        """
        return self._run_query(self.get_descendants, sub, obj)

    @staticmethod
    def _run_query(func: typing.Callable[[NODE], typing.Iterable[NODE]],
                   sub: typing.Union[str, NODE, Identified],
                   obj: typing.Union[str, NODE, Identified]) -> bool:
        sub = OntologyGraph._map_to_term_id(sub)
        obj = OntologyGraph._map_to_term_id(obj)
        return any(sub == term_id for term_id in func(obj))

    @abc.abstractmethod
    def __contains__(self, item: NODE) -> bool:
        pass

    @abc.abstractmethod
    def __iter__(self) -> typing.Iterator[NODE]:
        pass

    @staticmethod
    def _map_to_term_id(item: typing.Union[str, NODE, Identified]) -> TermId:
        if isinstance(item, Identified):
            return item.identifier
        elif isinstance(item, str):
            return TermId.from_curie(item)
        elif isinstance(item, TermId):
            return item
        else:
            raise ValueError(f'Expected `str`, `TermId` or `Identified` but got `{type(item)}`')


class GraphAware(typing.Generic[NODE], metaclass=abc.ABCMeta):
    """
    Base class for entities that have an `OntologyGraph`.
    """

    @property
    @abc.abstractmethod
    def graph(self) -> OntologyGraph[NODE]:
        """
        :return: the ontology graph with nodes of a given type.
        """
        pass
