"""
The `hpotk.ontology` package defines what an ontology is and provides methods for working with ontology data.
"""

from ._api import MinimalOntology, Ontology
from ._default import create_minimal_ontology, create_ontology

__all__ = [
    "MinimalOntology",
    "Ontology",
    "create_minimal_ontology",
    "create_ontology",
]
