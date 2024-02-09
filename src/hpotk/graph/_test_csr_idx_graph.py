import typing

import pytest

import hpotk
from ._csr_idx_graph import CsrIndexedOntologyGraph
from ._factory import CsrIndexedGraphFactory


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


class TestCsrIndexedOntologyGraph:
    """
    Assuming `CsrIndexedGraphFactory` is correct, here we test the HPO traversal and others.
    """

    @pytest.fixture
    def graph(self, edges: typing.Sequence[typing.Tuple[hpotk.TermId, hpotk.TermId]]) -> CsrIndexedOntologyGraph:
        factory = CsrIndexedGraphFactory()
        return factory.create_graph(edges)

    def test_root(self, graph: CsrIndexedOntologyGraph):
        assert graph.root == hpotk.TermId.from_curie('HP:1')

    @pytest.mark.parametrize(
        'source, expected',
        [
            ("HP:1", {"HP:01", "HP:02", "HP:03"}),
            ("HP:01", {"HP:010", "HP:011"}),
            ("HP:010", {"HP:0110"}),
            ("HP:011", {"HP:0110"}),
            ("HP:0110", {}),

            ("HP:02", {"HP:020", "HP:021", "HP:022"}),

            ("HP:03", {}),
        ]
    )
    def test_get_children(self, graph: CsrIndexedOntologyGraph,
                          source: str, expected: typing.Set[str]):
        actual = set(graph.get_children(hpotk.TermId.from_curie(source)))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)

    @pytest.mark.parametrize(
        'source, expected',
        [
            ("HP:1", {"HP:01", "HP:010", "HP:011", "HP:0110", "HP:02", "HP:020", "HP:021", "HP:022", "HP:03"}),
            ("HP:01", {"HP:010", "HP:011", "HP:0110"}),
            ("HP:010", {"HP:0110"}),
            ("HP:011", {"HP:0110"}),
            ("HP:0110", {}),

            ("HP:02", {"HP:020", "HP:021", "HP:022"}),

            ("HP:03", {}),
        ]
    )
    def test_get_descendants(self, graph: CsrIndexedOntologyGraph,
                             source: str, expected: typing.Set[str]):
        actual = set(graph.get_descendants(hpotk.TermId.from_curie(source)))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)

    @pytest.mark.parametrize(
        'source, expected',
        [
            ("HP:1", {"HP:01", "HP:010", "HP:011", "HP:0110", "HP:02", "HP:020", "HP:021", "HP:022", "HP:03", "HP:1"}),
            ("HP:01", {"HP:010", "HP:011", "HP:0110", "HP:01"}),
            ("HP:010", {"HP:0110", "HP:010"}),
            ("HP:011", {"HP:0110", "HP:011"}),
            ("HP:0110", {"HP:0110"}),

            ("HP:02", {"HP:020", "HP:021", "HP:022", "HP:02"}),

            ("HP:03", {"HP:03"}),
        ]
    )
    def test_get_descendants_incl_source(self, graph: CsrIndexedOntologyGraph,
                                         source: str, expected: typing.Set[str]):
        actual = set(graph.get_descendants(hpotk.TermId.from_curie(source), include_source=True))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)

    @pytest.mark.parametrize(
        'source, expected',
        [
            ("HP:1", {}),
            ("HP:01", {"HP:1"}),
            ("HP:010", {"HP:01"}),
            ("HP:0110", {"HP:010", "HP:011"}),

            ("HP:03", {"HP:1"}),
        ]
    )
    def test_get_parents(self, graph: CsrIndexedOntologyGraph,
                         source: str, expected: typing.Set[str]):
        actual = set(graph.get_parents(hpotk.TermId.from_curie(source)))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)

    @pytest.mark.parametrize(
        'source, expected',
        [
            ("HP:1", {}),
            ("HP:01", {"HP:1"}),
            ("HP:010", {"HP:1", "HP:01"}),
            ("HP:0110", {"HP:1", "HP:01", "HP:010", "HP:011"}),

            ("HP:03", {"HP:1"}),
        ]
    )
    def test_get_ancestors(self, graph: CsrIndexedOntologyGraph,
                           source: str, expected: typing.Set[str]):
        actual = set(graph.get_ancestors(hpotk.TermId.from_curie(source)))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)

    @pytest.mark.parametrize(
        'source, expected',
        [
            ("HP:1", {"HP:1"}),
            ("HP:01", {"HP:1", "HP:01"}),
            ("HP:010", {"HP:1", "HP:01", "HP:010"}),
            ("HP:0110", {"HP:1", "HP:01", "HP:010", "HP:011", "HP:0110"}),

            ("HP:03", {"HP:1", "HP:03"}),
        ]
    )
    def test_get_ancestors_incl_source(self, graph: CsrIndexedOntologyGraph,
                                       source: str, expected: typing.Set[str]):
        actual = set(graph.get_ancestors(hpotk.TermId.from_curie(source), include_source=True))

        assert actual == set(hpotk.TermId.from_curie(curie) for curie in expected)
