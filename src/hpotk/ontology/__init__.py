"""
Classes and methods for working with ontology data.
"""

from ._api import MinimalOntology, Ontology
from ._default import create_minimal_ontology, create_ontology
from . import load

__all__ = [
    'MinimalOntology', 'Ontology',
    'create_minimal_ontology', 'create_ontology'
]
