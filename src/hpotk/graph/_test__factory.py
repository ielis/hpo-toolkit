import typing

import numpy as np
import pytest

import hpotk
from ._csr_graph import OntologyGraph
from ._csr_idx_graph import IndexedOntologyGraph
from ._factory import IncrementalCsrGraphFactory, CsrIndexedGraphFactory
from ._factory import make_row_col_data


@pytest.fixture
def nodes() -> typing.Sequence[hpotk.TermId]:
    """
    Nodes for testing.
    """
    # Nodes are sorted.
    return (
        hpotk.TermId.from_curie('HP:01'),
        hpotk.TermId.from_curie('HP:010'),
        hpotk.TermId.from_curie('HP:011'),
        hpotk.TermId.from_curie('HP:0110'),
        hpotk.TermId.from_curie('HP:02'),
        hpotk.TermId.from_curie('HP:020'),
        hpotk.TermId.from_curie('HP:021'),
        hpotk.TermId.from_curie('HP:022'),
        hpotk.TermId.from_curie('HP:03'),
        hpotk.TermId.from_curie('HP:1'),
    )


@pytest.fixture
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


class TestFunctions:
    """
    Test the functions of the `_factory.py` file.
    """

    def test_make_row_col_data(self, nodes: typing.Sequence[hpotk.TermId],
                               edges: typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]):
        """
        We must get these `row`, `col`, and `data` values from given `nodes` and `edges`.
        """
        row, col, data = make_row_col_data(nodes, edges)

        assert row == [0, 3, 5, 7, 9, 13, 14, 15, 16, 17, 20]
        assert col == [1, 2, 9, 0, 3, 0, 3, 1, 2, 5, 6, 7, 9, 4, 4, 4, 9, 0, 4, 8]
        assert data == [-1, -1, 1, 1, -1, 1, -1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, -1, -1, -1]

    @pytest.mark.skip
    def test_compare_with_scipy(self, nodes: typing.Sequence[hpotk.TermId],
                                edges: typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]):
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
        row, col, data = make_row_col_data(nodes, edges)

        np.array_equal(csr.indptr, row)
        np.array_equal(csr.indices, col)
        np.array_equal(csr.data, data)


class TestIncrementalCsrGraphFactory:

    @pytest.fixture
    def factory(self) -> IncrementalCsrGraphFactory:
        return IncrementalCsrGraphFactory()

    def test_create_graph(self, factory: IncrementalCsrGraphFactory,
                          nodes: typing.Sequence[hpotk.TermId],
                          edges: typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]
                          ):
        graph = factory.create_graph(edges)
        assert graph.root == hpotk.TermId.from_curie('HP:1')


class TestTraversalOfIncrementalCsrGraphFactory:

    @pytest.fixture
    def factory(self) -> IncrementalCsrGraphFactory:
        return IncrementalCsrGraphFactory()

    @pytest.fixture
    def graph(self, factory: IncrementalCsrGraphFactory,
              edges: typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]) -> OntologyGraph:
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
    def test_get_children(self, graph: OntologyGraph,
                          source: str, expected: typing.Set[str]):
        children = set(graph.get_children(hpotk.TermId.from_curie(source)))
        assert children == set((hpotk.TermId.from_curie(curie) for curie in expected))

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
    def test_get_parents(self, graph: OntologyGraph,
                         source: str, expected: typing.Set[str]):
        children = set(graph.get_parents(hpotk.TermId.from_curie(source)))
        assert children == set((hpotk.TermId.from_curie(curie) for curie in expected))


class TestCsrIndexedGraphFactory:

    @pytest.fixture
    def factory(self) -> CsrIndexedGraphFactory:
        return CsrIndexedGraphFactory()

    def test_create_graph(self, factory: CsrIndexedGraphFactory,
                          edges: typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]):
        graph: IndexedOntologyGraph = factory.create_graph(edges)

        assert isinstance(graph, IndexedOntologyGraph)
        # We test the functionality elsewhere
