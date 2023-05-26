import unittest

import ddt
import numpy as np

from hpotk.model import TermId
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
