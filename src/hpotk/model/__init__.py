"""
The `hpotk.model` package provides data structures for working with ontology data.
"""

import typing

from ._term_id import TermId
from ._base import Identified, ObservableFeature, FrequencyAwareFeature, Named, Versioned, MetadataAware
from ._term import MinimalTerm, Term, Synonym, SynonymType, SynonymCategory

# Types
ID = typing.TypeVar('ID', bound=TermId)
CURIE_OR_TERM_ID = typing.Union[str, ID]
CURIE_OR_TERM_ID_OR_IDENTIFIED = typing.Union[str, TermId, Identified]
MINIMAL_TERM = typing.TypeVar('MINIMAL_TERM', bound=MinimalTerm)
TERM = typing.TypeVar('TERM', bound=Term)

__all__ = [
    'TermId', 'MinimalTerm', 'Term',
    'Identified', 'ObservableFeature', 'FrequencyAwareFeature', 'Named', 'Versioned', 'MetadataAware',
    'Synonym', 'SynonymType', 'SynonymCategory',
    'ID', 'CURIE_OR_TERM_ID', 'CURIE_OR_TERM_ID_OR_IDENTIFIED', 'MINIMAL_TERM', 'TERM'
]
