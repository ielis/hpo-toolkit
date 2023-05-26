import abc
import typing

from hpotk.model import TermId

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
    def get_children(self, source: NODE, include_source: bool = False) -> typing.Iterable[NODE]:
        """
        Get an iterable with the children of the `source` node.
        """
        pass

    @abc.abstractmethod
    def get_descendants(self, source: NODE, include_source: bool = False) -> typing.Iterable[NODE]:
        """
        Get an iterable with the descendants of the `source` node.
        """
        pass

    @abc.abstractmethod
    def get_parents(self, source: NODE, include_source: bool = False) -> typing.Iterable[NODE]:
        """
        Get an iterable with the parents of the `source` node.
        """
        pass

    @abc.abstractmethod
    def get_ancestors(self, source: NODE, include_source: bool = False) -> typing.Iterable[NODE]:
        """
        Get an iterable with the ancestors of the `source` node.
        """
        pass

    def is_leaf(self, node: NODE) -> bool:
        """
        Return `True` if the `node` is a leaf node - a node with no descendants.
        """
        for _ in self.get_descendants(node):
            return False
        return True

    def is_parent_of(self, sub: NODE, obj: NODE) -> bool:
        """
        Return `True` if the subject `sub` is a parent of the object `obj`.

        :param sub: a graph node.
        :param obj: other graph node.
        :return: `True` if the `sub` is a parent of the `obj`.
        """
        return self._run_query(self.get_parents, sub, obj)

    def is_ancestor_of(self, sub: NODE, obj: NODE) -> bool:
        """
        Return `True` if the subject `sub` is an ancestor of the object `obj`.

        :param sub: a graph node.
        :param obj: other graph node.
        :return: `True` if the `sub` is an ancestor of the `obj`.
        """
        return self._run_query(self.get_ancestors, sub, obj)

    def is_child_of(self, sub: NODE, obj: NODE) -> bool:
        """
        Return `True` if the `sub` is a child of the `obj`.

        :param sub: a graph node.
        :param obj: other graph node.
        :return: `True` if the `sub` is a child of the `obj`.
        """
        return self._run_query(self.get_children, sub, obj)

    def is_descendant_of(self, sub: NODE, obj: NODE) -> bool:
        """
        Return `True` if the `sub` is a descendant of the `obj`.

        :param sub: a graph node.
        :param obj: other graph node.
        :return: `True` if the `sub` is a descendant of the `obj`.
        """
        return self._run_query(self.get_descendants, sub, obj)

    @staticmethod
    def _run_query(func: typing.Callable[[NODE], typing.Iterable[NODE]],
                   sub: NODE,
                   obj: NODE) -> bool:
        return any(sub == term_id for term_id in func(obj))

    @abc.abstractmethod
    def __contains__(self, item: NODE) -> bool:
        pass

    @abc.abstractmethod
    def __iter__(self) -> typing.Iterator[NODE]:
        pass


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
