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

    .. note::

      `OntologyGraph` provides **iterators** for traversals instead of sets, lists, etc.
      See :ref:`iterable-vs-iterator` to learn why.
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
                     include_source: bool = False) -> typing.Iterator[NODE]:
        """
        Get an iterator with the children of the `source` node.

        :param source: a :class:`TermId`, an item that *has* a :class:`TermId` (:class:`Identified`), or a curie `str`
          representing the source node.
        :param include_source: `True` if the `source` should be included among the children, `False` otherwise.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_descendants(self, source: typing.Union[str, NODE, Identified],
                        include_source: bool = False) -> typing.Iterator[NODE]:
        """
        Get an iterator with the descendants of the `source` node.

        :param source: a :class:`TermId`, an item that *has* a :class:`TermId` (:class:`Identified`), or a curie `str`
          representing the source node.
        :param include_source: `True` if the `source` should be included among the descendants, `False` otherwise.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_parents(self, source: typing.Union[str, NODE, Identified],
                    include_source: bool = False) -> typing.Iterator[NODE]:
        """
        Get an iterator with the parents of the `source` node.

        :param source: a :class:`TermId`, an item that *has* a :class:`TermId` (:class:`Identified`), or a curie `str`
          representing the source node.
        :param include_source: `True` if the `source` should be included among the parents, `False` otherwise.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_ancestors(self, source: typing.Union[str, NODE, Identified],
                      include_source: bool = False) -> typing.Iterator[NODE]:
        """
        Get an iterator with the ancestors of the `source` node.

        :param source: a :class:`TermId`, an item that *has* a :class:`TermId` (:class:`Identified`), or a curie `str`
          representing the source node.
        :param include_source: `True` if the `source` should be included among the ancestors, `False` otherwise.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    def is_leaf(self, node: typing.Union[str, NODE, Identified]) -> bool:
        """
        Test if the node is a leaf - a node with no children.

        :return: `True` if the `node` is a leaf node or `False` otherwise.
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

    def compute_edge_distance(self, left: typing.Union[str, NODE, Identified],
                              right: typing.Union[str, NODE, Identified]) -> int:
        """
        Calculate the edge distance as the number of edges in the shortest path between the graph nodes.

        Distance of a node to itself is `0`.

        :param left: a graph node.
        :param right: other graph node.
        :return: a non-negative `int` of the edge distance.
        """
        left = OntologyGraph._map_to_term_id(left)
        right = OntologyGraph._map_to_term_id(right)
        if left == right:
            return 0  # Distance to self is `0`.

        left_dist = get_ancestor_distances(self, left)
        right_dist = get_ancestor_distances(self, right)
        return find_minimum_distance(left_dist, right_dist)

    @staticmethod
    def _run_query(func: typing.Callable[[NODE], typing.Iterator[NODE]],
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


def find_minimum_distance(left_dist: typing.Mapping[TermId, int],
                          right_dist: typing.Mapping[TermId, int]) -> int:
    dist = None
    for shared in left_dist.keys() & right_dist.keys():
        current = left_dist[shared] + right_dist[shared]
        if dist is None:
            dist = current
        else:
            dist = min(dist, current)

    return dist


def get_ancestor_distances(graph, src: TermId) -> typing.Mapping[TermId, int]:
    distances = {}
    seen = set()

    stack = [(0, src)]
    while stack:
        distance, term_id = stack.pop()

        current = distance + 1
        for parent in graph.get_parents(term_id):
            if parent not in seen:
                stack.append((current, parent))
            seen.add(parent)

        if term_id in distances:
            # We must keep the shortest distance
            distances[term_id] = min(distances[term_id], distance)
        else:
            distances[term_id] = distance

    return distances


class GraphAware(typing.Generic[NODE], metaclass=abc.ABCMeta):
    """
    A mixin class for entities that have an :class:`OntologyGraph`.
    """

    @property
    @abc.abstractmethod
    def graph(self) -> OntologyGraph[NODE]:
        """
        Get the ontology graph.
        """
        pass
