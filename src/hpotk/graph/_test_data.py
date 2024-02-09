import typing

import numpy as np

from hpotk.model import TermId

from ._api import OntologyGraph

from ._csr_graph import BisectPoweredCsrOntologyGraph
from .csr import ImmutableCsrMatrix


def get_toy_graph() -> typing.Tuple[typing.Sequence[TermId], OntologyGraph]:
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

    return nodes, BisectPoweredCsrOntologyGraph(root, nodes, am)