import unittest

import ddt
import numpy as np

from hpotk.model import TermId, Identified
from ._csr_graph import BisectPoweredCsrOntologyGraph
from .csr import ImmutableCsrMatrix


@ddt.ddt
class TestCsrOntologyGraph(unittest.TestCase):
    """
    Tests of the `OntologyGraph` API that just happen to be using `BisectPoweredCsrOntologyGraph` as the implementation.
    """

    NODES: np.ndarray
    GRAPH: BisectPoweredCsrOntologyGraph

    @classmethod
    def setUpClass(cls) -> None:
        root = TermId.from_curie('HP:1')
        curies = [
            'HP:01', 'HP:010', 'HP:011', 'HP:0110',
            'HP:02', 'HP:020', 'HP:021', 'HP:022',
            'HP:03', 'HP:1'
        ]
        nodes = np.fromiter(map(TermId.from_curie, curies), dtype=object)
        row = [0, 3, 5, 7, 9, 13, 14, 15, 16, 17, 20]
        col = [1, 2, 9, 0, 3, 0, 3, 1, 2, 5, 6, 7, 9, 4, 4, 4, 9, 0, 4, 8]
        data = [-1, -1, 1, 1, -1, 1, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1]
        am = ImmutableCsrMatrix(row, col, data, shape=(len(nodes), len(nodes)), dtype=int)

        cls.NODES = nodes
        cls.GRAPH = BisectPoweredCsrOntologyGraph(root, nodes, am)

    @ddt.data(
        # True examples
        ('HP:01', 'HP:1', True),

        ('HP:010', 'HP:01', True),
        ('HP:011', 'HP:01', True),
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
    )
    @ddt.unpack
    def test_is_child_of(self, sub, obj, expected):
        sub = TermId.from_curie(sub)
        obj = TermId.from_curie(obj)

        self.assertEqual(expected, self.GRAPH.is_child_of(sub, obj))

    @ddt.data(
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
    )
    @ddt.unpack
    def test_is_descendant_of(self, sub, obj, expected):
        sub = TermId.from_curie(sub)
        obj = TermId.from_curie(obj)

        self.assertEqual(expected, self.GRAPH.is_descendant_of(sub, obj))

    @ddt.data(
        # True examples
        ('HP:1', 'HP:01', True),

        ('HP:01', 'HP:010', True),
        ('HP:01', 'HP:011', True),
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
    )
    @ddt.unpack
    def test_is_parent_of(self, sub, obj, expected):
        sub = TermId.from_curie(sub)
        obj = TermId.from_curie(obj)

        self.assertEqual(expected, self.GRAPH.is_parent_of(sub, obj))

    @ddt.data(
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
    )
    @ddt.unpack
    def test_is_ancestor_of(self, sub, obj, expected):
        sub = TermId.from_curie(sub)
        obj = TermId.from_curie(obj)

        self.assertEqual(expected, self.GRAPH.is_ancestor_of(sub, obj))

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
                            {TermId.from_curie('HP:01'), TermId.from_curie('HP:1')})
        self.assertSetEqual(set(self.GRAPH.get_parents(SimpleIdentified.from_curie('HP:01'))),
                            {TermId.from_curie('HP:1')})
        self.assertSetEqual(set(self.GRAPH.get_children(SimpleIdentified.from_curie('HP:01'))),
                            {TermId.from_curie('HP:010'), TermId.from_curie('HP:011')})
        self.assertSetEqual(set(self.GRAPH.get_descendants(SimpleIdentified.from_curie('HP:01'))),
                            {TermId.from_curie('HP:010'), TermId.from_curie('HP:011'), TermId.from_curie('HP:0110')})

    def test_graph_queries_work_with_str(self):
        # tests
        self.assertTrue(self.GRAPH.is_ancestor_of('HP:01', 'HP:0110'))
        self.assertTrue(self.GRAPH.is_parent_of('HP:01', 'HP:010'))
        self.assertTrue(self.GRAPH.is_child_of('HP:01', 'HP:1'))
        self.assertTrue(self.GRAPH.is_descendant_of('HP:01', 'HP:1'))
        self.assertTrue(self.GRAPH.is_leaf('HP:03'))

        # traversal
        self.assertSetEqual(set(self.GRAPH.get_ancestors('HP:010')),
                            {TermId.from_curie('HP:01'), TermId.from_curie('HP:1')})
        self.assertSetEqual(set(self.GRAPH.get_parents('HP:01')),
                            {TermId.from_curie('HP:1')})
        self.assertSetEqual(set(self.GRAPH.get_children('HP:01')),
                            {TermId.from_curie('HP:010'), TermId.from_curie('HP:011')})
        self.assertSetEqual(set(self.GRAPH.get_descendants('HP:01')),
                            {TermId.from_curie('HP:010'), TermId.from_curie('HP:011'), TermId.from_curie('HP:0110')})

    @ddt.data(
        ('is_parent_of',),
        ('is_ancestor_of',),
        ('is_child_of',),
        ('is_descendant_of',),
    )
    @ddt.unpack
    def test_query_methods_with_unknown_source(self, func_name):
        existing = TermId.from_curie('HP:1')
        unknown = TermId.from_curie('HP:999')

        func = getattr(self.GRAPH, func_name)
        with self.assertRaises(ValueError) as ctx:
            func(existing, unknown)
        self.assertEqual('Term ID not found in the graph: HP:999', ctx.exception.args[0])


class SimpleIdentified(Identified):

    @staticmethod
    def from_curie(curie: str):
        return SimpleIdentified(TermId.from_curie(curie))

    def __init__(self, identifier: TermId):
        self._id = identifier

    @property
    def identifier(self) -> TermId:
        return self._id
