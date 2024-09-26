import re
import json
import typing
import logging

from hpotk.model import TermId, MinimalTerm, Term
from hpotk.graph import OntologyGraph
from hpotk.graph import GraphFactory, CsrIndexedGraphFactory, OWL_THING
from hpotk.ontology import MinimalOntology, Ontology, create_ontology, create_minimal_ontology
from hpotk.util import open_text_io_handle_for_reading

from ._model import create_node, create_edge
from ._model import Node, Edge, NodeType
from ._factory import MinimalTermFactory, TermFactory, ObographsTermFactory, MINIMAL_TERM

logger = logging.getLogger(__name__)

# TODO: verify PURL works for other ontologies than HPO
# TODO: thoroughly test the PURL pattern
# A pattern to match an obolibrary PURL. The PURL should is expected to have 3 parts: `prefix`, `id`, and `curie`
# The `curie` is `prefix` + '_' + `id`.
PURL_PATTERN = re.compile(r'http://purl\.obolibrary\.org/obo/(?P<curie>(?P<prefix>\w+)_(?P<id>\w+))')
DATE_PATTERN = re.compile(r'.*/(?P<date>\d{4}-\d{2}-\d{2})/.*')


def load_minimal_ontology(
        file: typing.Union[typing.IO, str],
        term_factory: ObographsTermFactory[MinimalTerm] = MinimalTermFactory(),
        graph_factory: GraphFactory = CsrIndexedGraphFactory(),
        prefixes_of_interest: typing.Set[str] = {'HP'},
) -> MinimalOntology:
    return _load_impl(
        file,
        term_factory, 
        graph_factory, 
        prefixes_of_interest, 
        create_minimal_ontology,
    )


def load_ontology(
        file: typing.Union[typing.IO, str],
        term_factory: ObographsTermFactory[Term] = TermFactory(),
        graph_factory: GraphFactory = CsrIndexedGraphFactory(),
        prefixes_of_interest: typing.Set[str] = {'HP'},
) -> Ontology:
    return _load_impl(
        file,
        term_factory, 
        graph_factory, 
        prefixes_of_interest, 
        create_ontology,
    )


def _load_impl(
        file: typing.Union[typing.IO, str],
        term_factory: ObographsTermFactory[MINIMAL_TERM],
        graph_factory: GraphFactory,
        prefixes_of_interest: typing.Set[str],
        ontology_creator,        
):
    obograph = get_obographs_graph(file)
    logger.debug("Extracting ontology terms")
    id_to_term_id, terms = extract_terms(
        obograph['nodes'], term_factory, 
        prefixes_of_interest=prefixes_of_interest,
    )
    logger.debug("Creating the edge list")
    edge_list = create_edge_list(obograph['edges'], id_to_term_id)
    logger.debug("Building ontology graph")
    ontology_graph: OntologyGraph = graph_factory.create_graph(edge_list)
    if ontology_graph.root == OWL_THING:
        # TODO: - consider adding Owl thing into terms list
        pass
    version = extract_ontology_version(obograph['meta'])
    logger.debug("Assembling the ontology")
    ontology = ontology_creator(ontology_graph, terms, version)
    logger.debug("Done")
    return ontology


def get_obographs_graph(file: typing.Union[typing.IO, str]):
    with open_text_io_handle_for_reading(file) as fh:
        document = json.load(fh)
    if not isinstance(document, dict):
        raise ValueError(f'The JSON document should have been a dict but was {type(document)}')
    if 'graphs' not in document:
        raise ValueError('Did not find the `graphs` attribute in the JSON document')
    graphs = document['graphs']
    if not isinstance(graphs, typing.Sequence):
        raise ValueError('`graphs` JSON attribute is not a sequence')
    if len(graphs) < 1:
        raise ValueError('`graphs` JSON attribute is empty')
    elif len(graphs) == 1:
        # The happy path
        return graphs[0]
    else:
        raise ValueError(f'We expect exactly 1 graph but there are {len(graphs)} graphs in the JSON document')


def extract_terms(
    nodes: typing.Iterable[dict],
    term_factory: ObographsTermFactory[MINIMAL_TERM],
    prefixes_of_interest: typing.Set[str],
) -> typing.Tuple[typing.Mapping[str, TermId], typing.Sequence[MINIMAL_TERM]]:
    curie_to_term: typing.Dict[str, TermId] = {}
    terms: typing.List[MINIMAL_TERM] = []
    for data in nodes:
        # 1) map data to `Node`
        node: typing.Optional[Node] = create_node(data)

        # 2) we only work with class Nodes
        if not node or node.type != NodeType.CLASS:
            continue

        # 3) check if PURL is OK
        curie = extract_curie_from_purl(node.id)
        if not curie:
            logger.debug('Unable to extract CURIE from PURL %s', node.id)
            continue
        term_id = TermId.from_curie(curie)
        if term_id.prefix not in prefixes_of_interest:
            logger.debug('Skipping not a term of interest %s', term_id.value)
            continue

        curie_to_term[curie] = term_id

        # 4) create the `Term`
        term = term_factory.create_term(term_id, node)
        if term:
            terms.append(term)

    return curie_to_term, terms


def create_edge_list(
        edges: typing.Iterable[typing.Dict[str, str]],
        curie_to_termid: typing.Mapping[str, TermId],
) -> typing.List[typing.Tuple[TermId, TermId]]:
    edge_list: typing.List[typing.Tuple[TermId, TermId]] = []
    for data in edges:
        edge: Edge = create_edge(data)

        # We only care about `is_a` relationships.
        if edge.pred != 'is_a':
            logger.debug('Skipping edge with pred %s!=\'is_a\'', edge.pred)
            continue

        # Get source and destination.
        src_curie = extract_curie_from_purl(edge.sub)
        if src_curie is None:
            logger.warning('Unable to extract CURIE from sub PURL %s', edge.sub)
            continue
        try:
            src: TermId = curie_to_termid[src_curie]
        except KeyError:
            logger.debug(
                'Skipping edge %s %s %s because subject %s was was not found in terms', 
                edge.sub, edge.pred, edge.obj, edge.sub,
            )
            continue

        dest_curie = extract_curie_from_purl(edge.obj)
        if dest_curie is None:
            logger.warning('Unable to extract CURIE from obj PURL %s', edge.obj)
            continue
        try:
            dest: TermId = curie_to_termid[dest_curie]
        except KeyError:
            logger.debug(
                'Skipping edge %s %s %s because object %s was was not found in terms', 
                edge.sub, edge.pred, edge.obj, edge.obj,
            )
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


def extract_ontology_version(meta: dict) -> typing.Optional[str]:
    if 'version' in meta:
        # A line like this:
        # 'http://purl.obolibrary.org/obo/hp/releases/2022-10-05/hp.json'
        match = DATE_PATTERN.search(meta['version'])
        if match:
            return match.group('date')
        else:
            logger.debug('Could not find a date pattern in version %s', meta["version"])
            return None
    elif 'basicPropertyValues' in meta:
        for bpv in meta['basicPropertyValues']:
            if 'pred' in bpv and 'val' in bpv:
                if bpv['pred'].endswith('#versionInfo'):
                    # An item like this:
                    # {
                    #   "pred": "http://www.w3.org/2002/07/owl#versionInfo",
                    #   "val": "2022-10-05"
                    # }
                    return bpv['val']

        logger.debug('Could not find basic property value with the version info')
        return None
    else:
        logger.debug('Could not determine the ontology version')
        return None
