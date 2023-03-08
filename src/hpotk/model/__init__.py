import typing

from ._term_id import TermId
from ._base import Identified, Named, Versioned
from ._term import MinimalTerm, Term

# Types
ID = typing.TypeVar('ID', bound=TermId)
CURIE_OR_TERM_ID = typing.Union[str, ID]
MINIMAL_TERM = typing.TypeVar('MINIMAL_TERM', bound=MinimalTerm)
TERM = typing.TypeVar('TERM', bound=Term)
