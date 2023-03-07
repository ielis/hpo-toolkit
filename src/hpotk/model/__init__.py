import typing

from ._term_id import TermId
from ._base import Identified, Named
from ._term import MinimalTerm, Term
from . import disease

# Types
ID = typing.TypeVar('ID', bound=TermId)
CURIE_OR_TERM_ID = typing.Union[str, ID]
MINIMAL_TERM = typing.TypeVar('MINIMAL_TERM', bound=MinimalTerm)
TERM = typing.TypeVar('TERM', bound=Term)
