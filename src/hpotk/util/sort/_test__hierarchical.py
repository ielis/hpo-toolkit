import ddt
import unittest

from hpotk import TermId, OntologyGraph

from hpotk.graph import IncrementalCsrGraphFactory

from ._hierarchical import HierarchicalSimilaritySorting


def make_ontology_graph() -> OntologyGraph:
    factory = IncrementalCsrGraphFactory()
    _, edges = make_nodes_and_edges()
    return factory.create_graph(edges)


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


@ddt.ddt
class TestSimilarityHierarchicalSorting(unittest.TestCase):
    GRAPH: OntologyGraph

    @classmethod
    def setUpClass(cls) -> None:
        cls.GRAPH = make_ontology_graph()

    def setUp(self) -> None:
        ics = {
            'HP:1': 0.,

            'HP:01': 1.,
            'HP:010': 2., 'HP:011': 2.3, 'HP:0110': 3.2,

            'HP:02': 1.5,
            'HP:020': 2.4, 'HP:021': 2.5, 'HP:022': 2.8,

            'HP:03': 2.
        }
        def ic_source(term_id: TermId) -> float: return ics.get(term_id.value, 0.)
        self.instance = HierarchicalSimilaritySorting(self.GRAPH, ic_source)

    @ddt.data(
        (('HP:021', 'HP:03', 'HP:01', 'HP:02', 'HP:1', 'HP:022', 'HP:0110', 'HP:020'),
         ('HP:0110', 'HP:01', 'HP:020', 'HP:022', 'HP:02', 'HP:021', 'HP:1', 'HP:03')),

        # Does not preserve order at the moment :'(.
        (('HP:0110', 'HP:01', 'HP:020', 'HP:022', 'HP:02', 'HP:021', 'HP:1', 'HP:03'),
         ('HP:01', 'HP:0110', 'HP:021', 'HP:02', 'HP:022',  'HP:020', 'HP:03', 'HP:1')),

        (('HP:021',),
         ('HP:021',))
    )
    @ddt.unpack
    def test_argsort(self, curies, expected):
        term_ids = tuple(map(TermId.from_curie, curies))

        term_idxs = self.instance.argsort(term_ids)

        ordered = tuple(term_ids[idx].value for idx in term_idxs)
        self.assertTupleEqual(expected, ordered)

