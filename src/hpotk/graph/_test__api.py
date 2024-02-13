import typing
import unittest

import ddt
import numpy as np
import pytest

import hpotk
from ._api import OntologyGraph, IndexedOntologyGraph
from ._csr_graph import BisectPoweredCsrOntologyGraph
from ._factory import CsrIndexedGraphFactory, IncrementalCsrGraphFactory
from .csr import ImmutableCsrMatrix


@pytest.fixture(scope='module')
def edges() -> typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]:
    # Edges for a graph with a single root node: HP:1
    return (
        # source -> destination
        (hpotk.TermId.from_curie('HP:01'), hpotk.TermId.from_curie('HP:1')),
        (hpotk.TermId.from_curie('HP:010'), hpotk.TermId.from_curie('HP:01')),
        (hpotk.TermId.from_curie('HP:011'), hpotk.TermId.from_curie('HP:01')),
        # This one is multi-parent.
        (hpotk.TermId.from_curie('HP:0110'), hpotk.TermId.from_curie('HP:010')),
        (hpotk.TermId.from_curie('HP:0110'), hpotk.TermId.from_curie('HP:011')),

        (hpotk.TermId.from_curie('HP:02'), hpotk.TermId.from_curie('HP:1')),
        (hpotk.TermId.from_curie('HP:020'), hpotk.TermId.from_curie('HP:02')),
        (hpotk.TermId.from_curie('HP:021'), hpotk.TermId.from_curie('HP:02')),
        (hpotk.TermId.from_curie('HP:022'), hpotk.TermId.from_curie('HP:02')),

        (hpotk.TermId.from_curie('HP:03'), hpotk.TermId.from_curie('HP:1')),
    )


@pytest.fixture(scope='module')
def indexed_graph(edges: typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]) -> IndexedOntologyGraph:
    factory = CsrIndexedGraphFactory()
    return factory.create_graph(edges)


@pytest.fixture(scope='module')
def base_graph(edges: typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]) -> OntologyGraph:
    factory = IncrementalCsrGraphFactory()
    return factory.create_graph(edges)


@pytest.mark.parametrize(
    'source, expected',
    [
        ("HP:1", {"HP:01", "HP:02", "HP:03"}),
        ("HP:01", {"HP:010", "HP:011"}),
        ("HP:010", {"HP:0110"}),
        ("HP:011", {"HP:0110"}),
        ("HP:0110", {}),

        ("HP:02", {"HP:020", "HP:021", "HP:022"}),

        ("HP:03", {})
    ]
)
class TestGetChildren:

    def test_get_children__indexed_graph(self,
                                         indexed_graph: IndexedOntologyGraph,
                                         source, expected):
        actual = set(indexed_graph.get_children(source))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)

    def test_get_children__base_graph(self,
                                      base_graph: OntologyGraph,
                                      source, expected):
        actual = set(base_graph.get_children(source))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)


@pytest.mark.parametrize(
    'source, expected',
    [
        ('HP:1', {'HP:01', 'HP:010', 'HP:011', 'HP:0110',
                  'HP:02', 'HP:020', 'HP:021', 'HP:022',
                  'HP:03'}),
        ('HP:01', {'HP:010', 'HP:011', 'HP:0110'}),
        ('HP:010', {'HP:0110'}),
        ('HP:011', {'HP:0110'}),
        ('HP:0110', set()),

        ('HP:02', {'HP:020', 'HP:021', 'HP:022'}),
        ('HP:020', set()),
        ('HP:021', set()),
        ('HP:022', set()),
        ('HP:03', set()),
    ]
)
class TestGetDescendants:

    def test_get_descendants__indexed_graph(self,
                                            indexed_graph: IndexedOntologyGraph,
                                            source, expected):
        actual = set(indexed_graph.get_descendants(source))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)

    def test_get_descendants__base_graph(self,
                                         base_graph: OntologyGraph,
                                         source, expected):
        actual = set(base_graph.get_descendants(source))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)


@pytest.mark.parametrize(
    'source, expected',
    [
        ("HP:1", {}),
        ("HP:01", {"HP:1"}),
        ("HP:010", {"HP:01"}),
        ("HP:0110", {"HP:010", "HP:011"}),

        ("HP:03", {"HP:1"})
    ]
)
class TestGetParents:

    def test_get_parents__indexed_graph(self,
                                        indexed_graph: IndexedOntologyGraph,
                                        source, expected):
        children = set(indexed_graph.get_parents(source))

        assert children == set(hpotk.TermId.from_curie(curie) for curie in expected)

    def test_get_parents__base_graph(self,
                                     base_graph: OntologyGraph,
                                     source, expected):
        actual = set(base_graph.get_parents(source))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)


@pytest.mark.parametrize(
    'source, expected',
    [
        ('HP:1', set()),
        ('HP:01', {'HP:1'}),
        ('HP:0110', {'HP:010', 'HP:011', 'HP:01', 'HP:1'}),
        ('HP:022', {'HP:02', 'HP:1'}),
        ('HP:03', {'HP:1'}),
    ]
)
class TestGetAncestors:

    def test_indexed_graph(self,
                           indexed_graph: IndexedOntologyGraph,
                           source, expected):
        actual = set(indexed_graph.get_ancestors(source))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)

    def test_base_graph(self,
                        base_graph: OntologyGraph,
                        source, expected):
        actual = set(base_graph.get_ancestors(source))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)


@pytest.mark.parametrize(
    'sub, obj, expected',
    [
        # True examples
        ('HP:1', 'HP:01', True),

        ('HP:01', 'HP:010', True),
        ('HP:01', 'HP:011', True),
        ('HP:010', 'HP:0110', True),
        ('HP:011', 'HP:0110', True),

        ('HP:1', 'HP:02', True),
        ('HP:02', 'HP:020', True),
        ('HP:02', 'HP:021', True),
        ('HP:02', 'HP:022', True),

        ('HP:1', 'HP:03', True),

        # False examples
        ('HP:1', 'HP:1', False),
        ('HP:02', 'HP:01', False),
        ('HP:01', 'HP:020', False),
        ('HP:0110', 'HP:03', False),
    ]
)
class TestIsParentOf:

    def test_indexed_graph(self,
                           indexed_graph: IndexedOntologyGraph,
                           sub, obj, expected):
        assert indexed_graph.is_parent_of(sub, obj) is expected

    def test_base_graph(self,
                        base_graph: OntologyGraph,
                        sub, obj, expected):
        assert base_graph.is_parent_of(sub, obj) is expected


@pytest.mark.parametrize(
    'sub, obj, expected',
    [
        # True examples
        ('HP:1', 'HP:010', True),
        ('HP:1', 'HP:011', True),
        ('HP:1', 'HP:0110', True),
        ('HP:01', 'HP:0110', True),

        ('HP:1', 'HP:020', True),
        ('HP:1', 'HP:021', True),
        ('HP:1', 'HP:022', True),

        # False examples
        ('HP:1', 'HP:1', False),
        ('HP:01', 'HP:1', False),
    ]
)
class TestIsAncestorOf:

    def test_indexed_graph(self,
                           indexed_graph: IndexedOntologyGraph,
                           sub, obj, expected):
        assert indexed_graph.is_ancestor_of(sub, obj) is expected

    def test_base_graph(self,
                        base_graph: OntologyGraph,
                        sub, obj, expected):
        assert base_graph.is_ancestor_of(sub, obj) is expected


@pytest.mark.parametrize(
    'sub, obj, expected',
    [
        # True examples
        ('HP:01', 'HP:1', True),

        ('HP:010', 'HP:01', True),
        ('HP:011', 'HP:01', True),
        ('HP:0110', 'HP:010', True),
        ('HP:0110', 'HP:011', True),

        ('HP:02', 'HP:1', True),
        ('HP:020', 'HP:02', True),
        ('HP:021', 'HP:02', True),
        ('HP:022', 'HP:02', True),

        ('HP:03', 'HP:1', True),

        # False examples
        ('HP:1', 'HP:1', False),
        ('HP:01', 'HP:02', False),
        ('HP:020', 'HP:01', False),
        ('HP:03', 'HP:0110', False),
    ]
)
class TestIsChildOf:

    def test_indexed_graph(self,
                           indexed_graph: IndexedOntologyGraph,
                           sub, obj, expected):
        assert indexed_graph.is_child_of(sub, obj) is expected

    def test_base_graph(self,
                        base_graph: OntologyGraph,
                        sub, obj, expected):
        assert base_graph.is_child_of(sub, obj) is expected


@pytest.mark.parametrize(
    'sub, obj, expected',
    [
        # True examples
        ('HP:010', 'HP:1', True),
        ('HP:011', 'HP:1', True),
        ('HP:0110', 'HP:1', True),
        ('HP:0110', 'HP:01', True),

        ('HP:020', 'HP:1', True),
        ('HP:021', 'HP:1', True),
        ('HP:022', 'HP:1', True),

        # False examples
        ('HP:1', 'HP:1', False),
        ('HP:1', 'HP:01', False),
    ]
)
class TestIsDescendantOf:

    def test_indexed_graph(self,
                           indexed_graph: IndexedOntologyGraph,
                           sub, obj, expected):
        assert indexed_graph.is_descendant_of(sub, obj) is expected

    def test_base_graph(self,
                        base_graph: OntologyGraph,
                        sub, obj, expected):
        assert base_graph.is_descendant_of(sub, obj) is expected


@pytest.mark.parametrize(
    'query, expected',
    [
        ('HP:1', False),

        ('HP:01', False),
        ('HP:010', False),
        ('HP:011', False),
        ('HP:0110', True),

        ('HP:02', False),
        ('HP:020', True),
        ('HP:021', True),
        ('HP:022', True),

        ('HP:03', True),
    ]
)
class TestIsLeaf:

    def test_indexed_graph(self,
                           indexed_graph: IndexedOntologyGraph,
                           query, expected):
        assert indexed_graph.is_leaf(query) is expected

    def test_base_graph(self,
                        base_graph: OntologyGraph,
                        query, expected):
        assert base_graph.is_leaf(query) is expected


@ddt.ddt
class TestCsrOntologyGraph(unittest.TestCase):
    """
    Tests of the `OntologyGraph` API that just happen to be using `BisectPoweredCsrOntologyGraph` as the implementation.
    """

    NODES: np.ndarray
    GRAPH: BisectPoweredCsrOntologyGraph

    @classmethod
    def setUpClass(cls) -> None:
        root = hpotk.TermId.from_curie('HP:1')
        curies = [
            'HP:01', 'HP:010', 'HP:011', 'HP:0110',
            'HP:02', 'HP:020', 'HP:021', 'HP:022',
            'HP:03', 'HP:1'
        ]
        nodes = np.fromiter(map(hpotk.TermId.from_curie, curies), dtype=object)
        row = [0, 3, 5, 7, 9, 13, 14, 15, 16, 17, 20]
        col = [1, 2, 9, 0, 3, 0, 3, 1, 2, 5, 6, 7, 9, 4, 4, 4, 9, 0, 4, 8]
        data = [-1, -1, 1, 1, -1, 1, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1]
        am = ImmutableCsrMatrix(row, col, data, shape=(len(nodes), len(nodes)), dtype=int)

        cls.NODES = nodes
        cls.GRAPH = BisectPoweredCsrOntologyGraph(root, nodes, am)

    def test_graph_queries_work_with_identified(self):
        # tests
        self.assertTrue(self.GRAPH.is_ancestor_of(SimpleIdentified.from_curie('HP:01'),
                                                  SimpleIdentified.from_curie('HP:0110')))
        self.assertTrue(self.GRAPH.is_parent_of(SimpleIdentified.from_curie('HP:01'),
                                                SimpleIdentified.from_curie('HP:010')))
        self.assertTrue(self.GRAPH.is_child_of(SimpleIdentified.from_curie('HP:01'),
                                               SimpleIdentified.from_curie('HP:1')))
        self.assertTrue(self.GRAPH.is_descendant_of(SimpleIdentified.from_curie('HP:01'),
                                                    SimpleIdentified.from_curie('HP:1')))
        self.assertTrue(self.GRAPH.is_leaf(SimpleIdentified.from_curie('HP:03')))

        # traversal
        self.assertSetEqual(set(self.GRAPH.get_ancestors(SimpleIdentified.from_curie('HP:010'))),
                            {hpotk.TermId.from_curie('HP:01'), hpotk.TermId.from_curie('HP:1')})
        self.assertSetEqual(set(self.GRAPH.get_parents(SimpleIdentified.from_curie('HP:01'))),
                            {hpotk.TermId.from_curie('HP:1')})
        self.assertSetEqual(set(self.GRAPH.get_children(SimpleIdentified.from_curie('HP:01'))),
                            {hpotk.TermId.from_curie('HP:010'), hpotk.TermId.from_curie('HP:011')})
        self.assertSetEqual(set(self.GRAPH.get_descendants(SimpleIdentified.from_curie('HP:01'))),
                            {hpotk.TermId.from_curie('HP:010'), hpotk.TermId.from_curie('HP:011'), hpotk.TermId.from_curie('HP:0110')})

    def test_graph_queries_work_with_str(self):
        # tests
        self.assertTrue(self.GRAPH.is_ancestor_of('HP:01', 'HP:0110'))
        self.assertTrue(self.GRAPH.is_parent_of('HP:01', 'HP:010'))
        self.assertTrue(self.GRAPH.is_child_of('HP:01', 'HP:1'))
        self.assertTrue(self.GRAPH.is_descendant_of('HP:01', 'HP:1'))
        self.assertTrue(self.GRAPH.is_leaf('HP:03'))

        # traversal
        self.assertSetEqual(set(self.GRAPH.get_ancestors('HP:010')),
                            {hpotk.TermId.from_curie('HP:01'), hpotk.TermId.from_curie('HP:1')})
        self.assertSetEqual(set(self.GRAPH.get_parents('HP:01')),
                            {hpotk.TermId.from_curie('HP:1')})
        self.assertSetEqual(set(self.GRAPH.get_children('HP:01')),
                            {hpotk.TermId.from_curie('HP:010'), hpotk.TermId.from_curie('HP:011')})
        self.assertSetEqual(set(self.GRAPH.get_descendants('HP:01')),
                            {hpotk.TermId.from_curie('HP:010'), hpotk.TermId.from_curie('HP:011'), hpotk.TermId.from_curie('HP:0110')})

    @ddt.data(
        ('is_parent_of',),
        ('is_ancestor_of',),
        ('is_child_of',),
        ('is_descendant_of',),
    )
    @ddt.unpack
    def test_query_methods_with_unknown_source(self, func_name):
        existing = hpotk.TermId.from_curie('HP:1')
        unknown = hpotk.TermId.from_curie('HP:999')

        func = getattr(self.GRAPH, func_name)
        with self.assertRaises(ValueError) as ctx:
            func(existing, unknown)
        self.assertEqual('Term ID not found in the graph: HP:999', ctx.exception.args[0])

    def test_traversal_methods_produce_iterators(self):
        whatever = hpotk.TermId.from_curie('HP:1')
        self.assertIsInstance(self.GRAPH.get_parents(whatever), typing.Iterator)
        self.assertIsInstance(self.GRAPH.get_children(whatever), typing.Iterator)
        self.assertIsInstance(self.GRAPH.get_ancestors(whatever), typing.Iterator)
        self.assertIsInstance(self.GRAPH.get_descendants(whatever), typing.Iterator)


class SimpleIdentified(hpotk.model.Identified):

    @staticmethod
    def from_curie(curie: str):
        return SimpleIdentified(hpotk.TermId.from_curie(curie))

    def __init__(self, identifier: hpotk.TermId):
        self._id = identifier

    @property
    def identifier(self) -> hpotk.TermId:
        return self._id
