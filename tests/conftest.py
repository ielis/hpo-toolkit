import os

import pytest
import hpotk

from pkg_resources import resource_filename

TOY_HPO = resource_filename(__name__, os.path.join('data', 'hp.toy.json'))


@pytest.fixture(scope='session')
def toy_hpo() -> hpotk.Ontology:
    return hpotk.load_ontology(TOY_HPO)
