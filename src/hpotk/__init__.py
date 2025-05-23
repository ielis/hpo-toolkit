"""
HPO toolkit is a library for working with Human Phenotype Ontology and the HPO annotation data.
"""

__version__ = "0.5.6.dev0"

from .graph import OntologyGraph, GraphAware
from .model import TermId, Term, MinimalTerm, Synonym, SynonymType, SynonymCategory
from .ontology import Ontology, MinimalOntology

from .ontology.load.obographs import load_minimal_ontology, load_ontology
from .store import OntologyType, OntologyStore, configure_ontology_store

__all__ = [
    "TermId", "MinimalTerm", "Term",
    "OntologyGraph", "GraphAware",
    "MinimalOntology", "Ontology",
    "OntologyStore", "OntologyType", "configure_ontology_store",
    "load_minimal_ontology", "load_ontology",
]
