import unittest

import ddt
import numpy as np

from hpotk.model import TermId
from ._csr_graph import SimpleCsrOntologyGraph
from ._factory import IncrementalCsrGraphFactory
from ._factory import make_row_col_data


def make_nodes_and_edges():
    """Prepare nodes and edges for testing."""
    # Nodes are sorted.
    nodes = [
        TermId.from_curie('HP:01'),
        TermId.from_curie('HP:010'),
        TermId.from_curie('HP:011'),
        TermId.from_curie('HP:0110'),
        TermId.from_curie('HP:02'),
        TermId.from_curie('HP:020'),
        TermId.from_curie('HP:021'),
        TermId.from_curie('HP:022'),
        TermId.from_curie('HP:03'),
        TermId.from_curie('HP:1'),
    ]

    # Edges for a graph with a single root node: HP:1
    edges = [
        # source -> destination
        (TermId.from_curie('HP:01'), TermId.from_curie('HP:1')),
        (TermId.from_curie('HP:010'), TermId.from_curie('HP:01')),
        (TermId.from_curie('HP:011'), TermId.from_curie('HP:01')),
        # This one is multi-parent.
        (TermId.from_curie('HP:0110'), TermId.from_curie('HP:010')),
        (TermId.from_curie('HP:0110'), TermId.from_curie('HP:011')),

        (TermId.from_curie('HP:02'), TermId.from_curie('HP:1')),
        (TermId.from_curie('HP:020'), TermId.from_curie('HP:02')),
        (TermId.from_curie('HP:021'), TermId.from_curie('HP:02')),
        (TermId.from_curie('HP:022'), TermId.from_curie('HP:02')),

        (TermId.from_curie('HP:03'), TermId.from_curie('HP:1')),
    ]
    return nodes, edges


class TestFunctions(unittest.TestCase):
    """
    Test the functions of the `_factory.py` file.
    """

    def test_make_row_col_data(self):
        """
        We must get these `row`, `col`, and `data` values from given `nodes` and `edges`.
        """
        nodes, edges = make_nodes_and_edges()

        row, col, data = make_row_col_data(nodes, edges)

        self.assertListEqual(row, [0, 3, 5, 7, 9, 13, 14, 15, 16, 17, 20])
        self.assertListEqual(col, [1, 2, 9, 0, 3, 0, 3, 1, 2, 5, 6, 7, 9, 4, 4, 4, 9, 0, 4, 8])
        self.assertListEqual(data, [-1, -1, 1, 1, -1, 1, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1])

    @unittest.skip
    def test_compare_with_scipy(self):
        """
        Compare that the row, col, data arrays are the same as those obtained from scipy.dense.csr_matrix when
        starting from a dense matrix.
        """
        # ############################## Expected values ##############################
        try:
            from scipy.sparse import csr_matrix
        except ImportError:
            raise Exception(f'We cannot run this test if scipy is not installed.')
        # This is the dense array that we expect for the nodes and edges created in `make_nodes_and_edges()`
        expected = np.array([[0, -1, -1, 0, 0, 0, 0, 0, 0, 1],
                             [1, 0, 0, -1, 0, 0, 0, 0, 0, 0],
                             [1, 0, 0, -1, 0, 0, 0, 0, 0, 0],
                             [0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, -1, -1, -1, 0, 1],
                             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
                             [1, 0, 0, 0, -1, 0, 0, 0, -1, 0]])
        csr = csr_matrix(expected)

        # ############################## Actual values ##############################
        row, col, data = make_row_col_data(*make_nodes_and_edges())

        np.array_equal(csr.indptr, row)
        np.array_equal(csr.indices, col)
        np.array_equal(csr.data, data)


class TestIncrementalCsrGraphFactory(unittest.TestCase):

    def setUp(self) -> None:
        self.factory = IncrementalCsrGraphFactory()

    def test_create_graph(self):
        nodes, edges = make_nodes_and_edges()

        graph = self.factory.create_graph(edges)
        self.assertEqual(graph.root, TermId.from_curie('HP:1'))


@ddt.ddt
class TestTraversalOfIncrementalCsrGraphFactory(unittest.TestCase):
    GRAPH: SimpleCsrOntologyGraph

    @classmethod
    def setUpClass(cls) -> None:
        nodes, edges = make_nodes_and_edges()
        factory = IncrementalCsrGraphFactory()
        cls.GRAPH: SimpleCsrOntologyGraph = factory.create_graph(edges)

    @ddt.data(
        ("HP:1", {"HP:01", "HP:02", "HP:03"}),
        ("HP:01", {"HP:010", "HP:011"}),
        ("HP:010", {"HP:0110"}),
        ("HP:011", {"HP:0110"}),
        ("HP:0110", {}),

        ("HP:02", {"HP:020", "HP:021", "HP:022"}),

        ("HP:03", {})
    )
    @ddt.unpack
    def test_get_children(self, source, expected):
        children = set(self.GRAPH.get_children(TermId.from_curie(source)))
        self.assertSetEqual(children, set([TermId.from_curie(curie) for curie in expected]))

    @ddt.data(
        ("HP:1", {}),
        ("HP:01", {"HP:1"}),
        ("HP:010", {"HP:01"}),
        ("HP:0110", {"HP:010", "HP:011"}),

        ("HP:03", {"HP:1"})
    )
    @ddt.unpack
    def test_get_parents(self, source, expected):
        children = set(self.GRAPH.get_parents(TermId.from_curie(source)))
        self.assertSetEqual(children, set([TermId.from_curie(curie) for curie in expected]))
