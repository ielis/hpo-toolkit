"""
The `hpotk.util.store` package provides
"""

from ._api import OntologyType, OntologyStore
from ._config import configure_ontology_store

__all__ = [
    'OntologyType', 'OntologyStore',
    'configure_ontology_store',
]
