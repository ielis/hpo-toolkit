"""
Data structures for modeling ontology data.
"""

import typing

from ._term_id import TermId
from ._base import Identified, ObservableFeature, FrequencyAwareFeature, Named, Versioned, MetadataAware
from ._term import MinimalTerm, Term, Synonym, SynonymType, SynonymCategory

# Types
ID = typing.TypeVar('ID', bound=TermId)
CURIE_OR_TERM_ID = typing.Union[str, ID]
MINIMAL_TERM = typing.TypeVar('MINIMAL_TERM', bound=MinimalTerm)
TERM = typing.TypeVar('TERM', bound=Term)

__all__ = ['TermId',
           'Identified', 'ObservableFeature', 'FrequencyAwareFeature', 'Named', 'Versioned', 'MetadataAware',
           'MinimalTerm', 'Term', 'Synonym', 'SynonymType', 'SynonymCategory']
