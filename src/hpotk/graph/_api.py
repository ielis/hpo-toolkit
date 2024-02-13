import abc
import itertools
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
        for _ in self.get_children(node):
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
        if isinstance(item, TermId):
            return item
        elif isinstance(item, Identified):
            return item.identifier
        elif isinstance(item, str):
            return TermId.from_curie(item)
        else:
            raise ValueError(f'Expected `TermId`, `Identified`, or `str` but got `{type(item)}`')


class IndexedOntologyGraph(typing.Generic[NODE], OntologyGraph[NODE], metaclass=abc.ABCMeta):
    """
    `IndexedOntologyGraph` allows working with ontology graph node indices instead of the ontology graph nodes.
    Working in the index space is generally faster, when used to traverse the graph or to create term id unions,
    differences, etc...

    Starting from a node index, `IndexedOntologyGraph` provides methods for getting indices of its children, descendants,
    parents, and ancestors. The node index can be obtained from :func:`node_to_idx`. Having an index, you can get
    the corresponding node using :func:`idx_to_node`.
    """

    @property
    @abc.abstractmethod
    def root_idx(self) -> int:
        """
        Get the index of the root node of the ontology graph.
        """
        pass

    @abc.abstractmethod
    def get_children_idx(self, source: int) -> typing.Sequence[int]:
        """
        Get an iterator with the indices of the children of the `source` node.

        :param source: an index of a node that represents the source node.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_descendant_idx(self, source: int) -> typing.Iterator[int]:
        """
        Get an iterator with the indices of the descendants of the `source` node.

        :param source: an index of a node that represents the source node.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_parents_idx(self, source: int) -> typing.Sequence[int]:
        """
        Get an iterator with the indices of the parents of the `source` node.

        :param source: an index of a node that represents the source node.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def get_ancestor_idx(self, source: int) -> typing.Iterator[int]:
        """
        Get an iterator with the indices of the ancestors of the `source` node.

        :param source: an index of a node that represents the source node.
        :raises ValueError: if `source` is not present in the graph.
        """
        pass

    @abc.abstractmethod
    def idx_to_node(self, idx: int) -> NODE:
        """
        Map the index into the corresponding node.

        :param idx: index to map to a node.
        :return: the node corresponding to the index.
        :raises ValueError: if `idx` does not correspond to any nodes of the ontology graph.
        """
        pass

    @abc.abstractmethod
    def node_to_idx(self, node: NODE) -> typing.Optional[int]:
        """
        Map the node into the corresponding node index.

        :param node: node to retrieve an index for.
        :return: the index corresponding to the `node` or `None` if the `node` is not in the graph.
        """
        pass

    # Override the `OntologyGraph` parts  ############################################################################ #

    @property
    def root(self) -> NODE:
        return self.idx_to_node(self.root_idx)

    def get_children(self, source: typing.Union[str, NODE, Identified],
                     include_source: bool = False) -> typing.Iterator[NODE]:
        return self._map_with_seq_func(source, include_source, self.get_children_idx)

    def get_descendants(self, source: typing.Union[str, NODE, Identified],
                        include_source: bool = False) -> typing.Iterator[NODE]:
        return self._map_with_iter_func(source, include_source, self.get_descendant_idx)

    def get_parents(self, source: typing.Union[str, NODE, Identified],
                    include_source: bool = False) -> typing.Iterator[NODE]:
        return self._map_with_seq_func(source, include_source, self.get_parents_idx)

    def get_ancestors(self, source: typing.Union[str, NODE, Identified],
                      include_source: bool = False) -> typing.Iterator[NODE]:
        return self._map_with_iter_func(source, include_source, self.get_ancestor_idx)

    def is_leaf(self, node: typing.Union[str, NODE, Identified]) -> bool:
        node_idx = self._map_to_term_idx(node)
        if node_idx is None:
            raise ValueError(f'No graph node found for {node}')

        for _ in self.get_children_idx(node_idx):
            return True
        return False

    def is_parent_of_idx(self, sub: int, obj: int) -> bool:
        """
        Return `True` if the subject `sub` is a parent of the object `obj`.

        :param sub: index of a graph node.
        :param obj: index of the other graph node.
        :return: `True` if the `sub` is a parent of the `obj`.
        :raises ValueError: if no such node exists for the `obj` index.
        """
        return any(sub == idx for idx in self.get_parents_idx(obj))

    def is_parent_of(self, sub: typing.Union[str, NODE, Identified],
                     obj: typing.Union[str, NODE, Identified]) -> bool:
        obj_idx = self._map_to_term_idx(obj)
        if obj_idx is None:
            raise ValueError(f'No graph node found for {obj}')

        sub_idx = self._map_to_term_idx(sub)
        if sub_idx is None:
            return False

        return any(sub_idx == idx for idx in self.get_parents_idx(obj_idx))

    def is_ancestor_of_idx(self, sub: int, obj: int) -> bool:
        """
        Return `True` if the subject `sub` is an ancestor of the object `obj`.

        :param sub: index of a graph node.
        :param obj: index of the other graph node.
        :return: `True` if the `sub` is an ancestor of the `obj`.
        :raises ValueError: if no such node exists for the `obj` index.
        """
        return any(sub == idx for idx in self.get_ancestor_idx(obj))

    def is_ancestor_of(self, sub: typing.Union[str, NODE, Identified],
                       obj: typing.Union[str, NODE, Identified]) -> bool:
        obj_idx = self._map_to_term_idx(obj)
        if obj_idx is None:
            raise ValueError(f'No graph node found for {obj}')

        sub_idx = self._map_to_term_idx(sub)
        if sub_idx is None:
            return False

        return any(sub_idx == idx for idx in self.get_ancestor_idx(obj_idx))

    def is_child_of_idx(self, sub: int, obj: int) -> bool:
        """
        Return `True` if the subject `sub` is a child of the object `obj`.

        :param sub: index of a graph node.
        :param obj: index of the other graph node.
        :return: `True` if the `sub` is a child of the `obj`.
        :raises ValueError: if no such node exists for the `sub` index.
        """
        # TODO: ValueError for `sub` may break the pattern
        return any(obj == idx for idx in self.get_parents_idx(sub))

    def is_child_of(self, sub: typing.Union[str, NODE, Identified],
                    obj: typing.Union[str, NODE, Identified]) -> bool:
        obj_idx = self._map_to_term_idx(obj)
        if obj_idx is None:
            raise ValueError(f'No graph node found for {obj}')

        sub_idx = self._map_to_term_idx(sub)
        if sub_idx is None:
            return False

        # Exploit the fact that a term has usually fewer parents than children.
        return any(obj_idx == idx for idx in self.get_parents_idx(sub_idx))

    def is_descendant_of_idx(self, sub: int, obj: int) -> bool:
        """
        Return `True` if the subject `sub` is a descendant of the object `obj`.

        :param sub: index of a graph node.
        :param obj: index of the other graph node.
        :return: `True` if the `sub` is a descendant of the `obj`.
        :raises ValueError: if no such node exists for the `sub` index.
        """
        # TODO: ValueError for `sub` may break the pattern
        return any(obj == idx for idx in self.get_ancestor_idx(sub))

    def is_descendant_of(self, sub: typing.Union[str, NODE, Identified],
                         obj: typing.Union[str, NODE, Identified]) -> bool:
        obj_idx = self._map_to_term_idx(obj)
        if obj_idx is None:
            raise ValueError(f'No graph node found for {obj}')

        sub_idx = self._map_to_term_idx(sub)
        if sub_idx is None:
            return False

        # Exploit the fact that a term has usually fewer parents than children.
        return any(obj_idx == idx for idx in self.get_ancestor_idx(sub_idx))

    def _map_with_iter_func(self, node: typing.Union[str, NODE, Identified],
                            include_source: bool,
                            func: typing.Callable[[int], typing.Iterator[int]]) -> typing.Iterator[NODE]:
        idx = self._map_to_term_idx(node)
        if idx is not None:
            if include_source:
                return itertools.chain(
                    (self.idx_to_node(idx),),
                    map(self.idx_to_node, func(idx)))
            else:
                return map(self.idx_to_node, func(idx))
        else:
            raise ValueError(f'{node} is not present in the graph!')

    def _map_with_seq_func(self, node: typing.Union[str, NODE, Identified],
                           include_source: bool,
                           func: typing.Callable[[int], typing.Sequence[int]]) -> typing.Iterator[NODE]:
        idx = self._map_to_term_idx(node)
        if idx is not None:
            if include_source:
                return itertools.chain(
                    (self.idx_to_node(idx),),
                    map(self.idx_to_node, func(idx)))
            else:
                return map(self.idx_to_node, func(idx))
        else:
            raise ValueError(f'{node} is not present in the graph!')

    def _map_to_term_idx(self, node: typing.Union[str, NODE, Identified]) -> typing.Optional[int]:
        """
        A convenience method to convert a `node` into the node index.

        :param node: one of the expected node types, including CURIE `str`, NODE, or an :class:`Identified` item.
        :return: the node index or `None` if the node is not present in the graph.
        :raises ValueError: if the node is not in one of the expected types.
        """
        term_id = self._map_to_term_id(node)
        return self.node_to_idx(term_id)

    # The rest

    def __contains__(self, item: NODE) -> bool:
        return self.node_to_idx(item) is not None


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
