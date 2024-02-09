import os

import pytest
import hpotk

from pkg_resources import resource_filename


@pytest.fixture(scope='session')
def fpath_toy_hpo() -> str:
    return resource_filename(__name__, os.path.join('data', 'hp.toy.json'))


@pytest.fixture(scope='session')
def fpath_toy_hpoa_older() -> str:
    return resource_filename(__name__, os.path.join('data', 'phenotype.fake.older.hpoa'))


@pytest.fixture(scope='session')
def fpath_toy_hpoa() -> str:
    return resource_filename(__name__, os.path.join('data', 'phenotype.fake.novel.hpoa'))


@pytest.fixture(scope='session')
def toy_hpo(fpath_toy_hpo: str) -> hpotk.Ontology:
    return hpotk.load_ontology(fpath_toy_hpo)


@pytest.fixture(scope='session')
def fpath_small_hpo() -> str:
    return resource_filename(__name__, os.path.join('data', 'hp.small.json'))


@pytest.fixture(scope='session')
def small_hpo(fpath_small_hpo: str) -> hpotk.Ontology:
    return hpotk.load_ontology(fpath_small_hpo)


@pytest.fixture(scope='session')
def fpath_real_shortlist_hpoa() -> str:
    return resource_filename(__name__, os.path.join('data', 'phenotype.real-shortlist.hpoa'))

