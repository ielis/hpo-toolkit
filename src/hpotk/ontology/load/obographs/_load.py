import re
import json
import typing
import logging

from hpotk.model import TermId, MinimalTerm, Term
from hpotk.graph import OntologyGraph
from hpotk.graph import GraphFactory, CsrGraphFactory, OWL_THING
from hpotk.ontology import MinimalOntology, Ontology, create_ontology, create_minimal_ontology
from hpotk.util import open_text_io_handle

from ._model import create_node, create_edge
from ._model import Node, Edge, NodeType
from ._factory import MinimalTermFactory, TermFactory, ObographsTermFactory, MINIMAL_TERM

logger = logging.getLogger(__name__)

# TODO - verify PURL works for other ontologies than HPO
# A pattern to match an obolibrary PURL. The PURL should is expected to have 3 parts: `prefix`, `id`, and `curie`
# The `curie` is `prefix` + '_' + `id`.
PURL_PATTERN = re.compile(r'http://purl\.obolibrary\.org/obo/(?P<curie>(?P<prefix>\w+)_(?P<id>\d{7}))')


def load_minimal_ontology(file: typing.Union[typing.IO, str],
                          term_factory: ObographsTermFactory[MinimalTerm] = MinimalTermFactory(),
                          graph_factory: GraphFactory = CsrGraphFactory()) -> MinimalOntology:
    return _load_impl(file, term_factory, graph_factory, create_minimal_ontology)


def load_ontology(file: typing.Union[typing.IO, str],
                  term_factory: ObographsTermFactory[Term] = TermFactory(),
                  graph_factory: GraphFactory = CsrGraphFactory()) -> Ontology:
    return _load_impl(file, term_factory, graph_factory, create_ontology)


def _load_impl(file: typing.Union[typing.IO, str],
               term_factory: ObographsTermFactory[MinimalTerm],
               graph_factory: GraphFactory,
               ontology_creator):
    hpo = get_hpo_graph(file)
    logger.debug("Extracting ontology terms")
    id_to_term_id, terms = extract_terms(hpo['nodes'], term_factory)
    logger.debug(f"Creating the edge list")
    edge_list = create_edge_list(hpo['edges'], id_to_term_id)
    logger.debug(f"Building ontology graph")
    graph: OntologyGraph = graph_factory.create_graph(edge_list)
    if graph.root == OWL_THING:
        # TODO - consider adding Owl thing into terms list
        pass
    version = None  # TODO - implement getting version!
    logger.debug(f"Assemblying the ontology")
    return ontology_creator(graph, terms, version)


def get_hpo_graph(file: typing.Union[typing.IO, str]):
    with open_text_io_handle(file) as fh:
        document = json.load(fh)
    if not isinstance(document, dict):
        raise ValueError(f'The JSON document should have been a dict but was {type(document)}')
    if 'graphs' not in document:
        raise ValueError(f'Did not find the `graphs` attribute in the JSON document')
    graphs = document['graphs']
    if not isinstance(graphs, typing.Sequence):
        raise ValueError(f'`graphs` JSON attribute is not a sequence')
    if len(graphs) < 1:
        raise ValueError(f'`graphs` JSON attribute is empty')
    elif len(graphs) == 1:
        # The happy path
        return graphs[0]
    else:
        raise ValueError(f'We expect exactly 1 graph but there are {len(graphs)} graphs in the JSON document')


def extract_terms(nodes: typing.Iterable[dict],
                  term_factory: ObographsTermFactory[MINIMAL_TERM]) \
        -> typing.Tuple[typing.Mapping[str, TermId], typing.Sequence[MINIMAL_TERM]]:
    curie_to_term: typing.Dict[str, TermId] = {}
    terms: typing.List[Term] = []
    for data in nodes:
        # 1) map data to `Node`
        node: Node = create_node(data)

        # 2) we only work with class Nodes
        if not node or node.type != NodeType.CLASS:
            continue

        # 3) check if PURL is OK
        curie = extract_curie_from_purl(node.id)
        if not curie:
            logger.debug(f'Unable to parse PURL {node.id} into CURIE')
            continue
        term_id = TermId.from_curie(curie)
        if term_id.prefix != 'HP':
            logger.debug(f'Skipping non-HPO term {term_id.value}')
            continue

        curie_to_term[curie] = term_id

        # 4) create the `Term`
        term = term_factory.create_term(term_id, node)
        if term:
            terms.append(term)

    return curie_to_term, terms


def create_edge_list(edges: typing.Iterable[typing.Dict[str, str]],
                     curie_to_termid: typing.Mapping[str, TermId]) -> typing.List[typing.Tuple[TermId, TermId]]:
    edge_list: typing.List[typing.Tuple[TermId, TermId]] = []
    for data in edges:
        edge: Edge = create_edge(data)

        # We only care about `is_a` relationships.
        if edge.pred != 'is_a':
            logger.debug(f'Skipping edge with pred {edge.pred}!=\'is_a\'')
            continue

        # Get source and destination.
        try:
            curie = extract_curie_from_purl(edge.sub)
            src: TermId = curie_to_termid[curie]
        except KeyError:
            logger.warning(f'Source edge {edge.sub} was not found in terms')
            # TODO - maybe we should even abort?
            continue

        try:
            curie: str = extract_curie_from_purl(edge.obj)
            dest: TermId = curie_to_termid[curie]
        except KeyError:
            logger.warning(f'Destination edge {edge.obj} was not found in terms')
            # TODO - maybe we should even abort?
            continue

        edge_list.append((src, dest))

    return edge_list


def extract_curie_from_purl(purl: str) -> typing.Optional[str]:
    """
    Parse HPO PURL (e.g. `http://purl.obolibrary.org/obo/HP_0002813`) into the CURIE (e.g. `HP_0002813`).

    Returns the CURIE `str` or `None` if the PURL is mis-formatted.
    """
    matcher = PURL_PATTERN.match(purl)
    return matcher.group('curie') if matcher else None
