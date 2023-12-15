import pytest

from hpotk import TermId, OntologyGraph
from hpotk.graph import IncrementalCsrGraphFactory
from ._hierarchical import HierarchicalIcTermIdSorting, HierarchicalEdgeTermIdSorting, EdgeSimilarityMeasure


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


@pytest.fixture
def ontology_graph() -> OntologyGraph:
    factory = IncrementalCsrGraphFactory()
    _, edges = make_nodes_and_edges()
    return factory.create_graph(edges)


class TestHierarchicalSimilaritySorting:

    @pytest.fixture
    def ic_sim_sorting(self, ontology_graph: OntologyGraph) -> HierarchicalIcTermIdSorting:
        ics = {
            'HP:1': 0.,

            'HP:01': 1.,
            'HP:010': 2., 'HP:011': 2.3, 'HP:0110': 3.2,

            'HP:02': 1.5,
            'HP:020': 2.4, 'HP:021': 2.5, 'HP:022': 2.8,

            'HP:03': 2.
        }

        def ic_source(term_id: TermId) -> float: return ics.get(term_id.value, 0.)

        return HierarchicalIcTermIdSorting(ontology_graph, ic_source)

    @pytest.mark.parametrize('curies, expected',
                             [
                                 (('HP:021', 'HP:03', 'HP:01', 'HP:02', 'HP:1', 'HP:022', 'HP:0110', 'HP:020'),
                                  ('HP:0110', 'HP:01', 'HP:020', 'HP:022', 'HP:02', 'HP:021', 'HP:1', 'HP:03')),

                                 # Does not preserve order at the moment :'(.
                                 (('HP:0110', 'HP:01', 'HP:020', 'HP:022', 'HP:02', 'HP:021', 'HP:1', 'HP:03'),
                                  ('HP:01', 'HP:0110', 'HP:021', 'HP:02', 'HP:022', 'HP:020', 'HP:03', 'HP:1')),

                                 (('HP:021',),
                                  ('HP:021',))
                             ]
                             )
    def test_argsort(self, curies, expected, ic_sim_sorting: HierarchicalIcTermIdSorting):
        term_ids = tuple(map(TermId.from_curie, curies))

        term_indices = ic_sim_sorting.argsort(term_ids)

        ordered = tuple(term_ids[idx].value for idx in term_indices)
        assert expected == ordered


class TestHierarchicalEdgeTermIdSorting:

    @pytest.fixture
    def edge_sim_sorting(self, ontology_graph: OntologyGraph) -> HierarchicalEdgeTermIdSorting:
        return HierarchicalEdgeTermIdSorting(ontology_graph)

    @pytest.mark.parametrize('curies, expected',
                             [
                                 (('HP:021', 'HP:03', 'HP:01', 'HP:02', 'HP:1', 'HP:022', 'HP:0110', 'HP:020'),
                                  ('HP:02', 'HP:021', 'HP:022', 'HP:020', 'HP:1', 'HP:03', 'HP:01', 'HP:0110')),

                                 # Does not preserve order at the moment :'(.
                                 (('HP:0110', 'HP:01', 'HP:020', 'HP:022', 'HP:02', 'HP:021', 'HP:1', 'HP:03'),
                                  ('HP:1', 'HP:01', 'HP:03', 'HP:02', 'HP:020', 'HP:022', 'HP:021', 'HP:0110')),

                                 (('HP:021',),
                                  ('HP:021',))
                             ]
                             )
    def test_argsort(self, curies, expected, edge_sim_sorting: HierarchicalEdgeTermIdSorting):
        term_ids = tuple(map(TermId.from_curie, curies))

        term_indices = edge_sim_sorting.argsort(term_ids)

        ordered = tuple(term_ids[idx].value for idx in term_indices)
        assert ordered == expected


class TestEdgeSimilarityMeasure:

    @pytest.fixture
    def edge_sim(self, ontology_graph: OntologyGraph) -> EdgeSimilarityMeasure:
        return EdgeSimilarityMeasure(ontology_graph)

    @pytest.mark.parametrize('left, right, common_ancestor, expected',
                             [
                                 ('HP:1', 'HP:1', 'HP:1', 0),
                                 ('HP:01', 'HP:01', 'HP:01', 0),
                                 ('HP:010', 'HP:0110', 'HP:010', 1),
                                 ('HP:011', 'HP:0110', 'HP:011', 1),
                                 ('HP:01', 'HP:0110', 'HP:01', 2),
                                 ('HP:1', 'HP:0110', 'HP:1', 3),
                                 ('HP:03', 'HP:01', 'HP:1', 2),
                                 ('HP:03', 'HP:02', 'HP:1', 2),
                                 ('HP:0110', 'HP:022', 'HP:1', 5),
                             ])
    def test_compute_edge_distance(self, left: str, right: str, common_ancestor: str, expected: int,
                                   edge_sim: EdgeSimilarityMeasure):
        left = TermId.from_curie(left)
        right = TermId.from_curie(right)
        common_ancestor = TermId.from_curie(common_ancestor)

        lr_dist, lr_term_id = edge_sim.calculate_edge_distance(left, right)
        assert lr_dist == expected
        rl_dist, rl_term_id = edge_sim.calculate_edge_distance(right, left)
        assert rl_dist == expected
        assert lr_term_id == rl_term_id
        assert lr_term_id == common_ancestor
