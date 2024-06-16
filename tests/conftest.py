import os

import pytest

import hpotk


# ####################################### Pytest options ############################################################# #

def pytest_addoption(parser):
    parser.addoption(
        "--runonline", action="store_true", default=False, help="run online tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "online: mark test that require internet access to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runonline"):
        # --runonline given in cli: do not skip online tests
        return
    skip_online = pytest.mark.skip(reason="need --runonline option to run")
    for item in items:
        if "online" in item.keywords:
            item.add_marker(skip_online)


# ####################################### Fixtures ################################################################### #


@pytest.fixture(scope='session')
def fpath_data() -> str:
    parent = os.path.dirname(__file__)
    return os.path.join(parent, 'data')


@pytest.fixture(scope='session')
def fpath_toy_hpo(fpath_data: str) -> str:
    return os.path.join(fpath_data, 'hp.toy.json')


@pytest.fixture(scope='session')
def fpath_toy_hpoa_older(fpath_data: str) -> str:
    return os.path.join(fpath_data, 'phenotype.fake.older.hpoa')


@pytest.fixture(scope='session')
def fpath_toy_hpoa(fpath_data: str) -> str:
    return os.path.join(fpath_data, 'phenotype.fake.novel.hpoa')


@pytest.fixture(scope='session')
def toy_hpo(fpath_toy_hpo: str) -> hpotk.Ontology:
    return hpotk.load_ontology(fpath_toy_hpo)


@pytest.fixture(scope='session')
def fpath_small_hpo(fpath_data: str) -> str:
    return os.path.join(fpath_data, 'hp.small.json')


@pytest.fixture(scope='session')
def small_hpo(fpath_small_hpo: str) -> hpotk.Ontology:
    return hpotk.load_ontology(fpath_small_hpo)


@pytest.fixture(scope='session')
def fpath_real_shortlist_hpoa(fpath_data: str) -> str:
    return os.path.join(fpath_data, 'phenotype.real-shortlist.hpoa')


@pytest.fixture(scope='session')
def fpath_real_maxo(fpath_data: str) -> str:
    return os.path.join(fpath_data, 'maxo.2024-05-24.json.gz')
