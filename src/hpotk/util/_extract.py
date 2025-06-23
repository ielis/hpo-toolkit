import typing

from hpotk.model import TermId, Identified


def extract_term_id(
    input: typing.Union[str, TermId, Identified],
) -> TermId:
    """
    Extract term ID from multiple `input` types.

    If the input is a `str`, then it is expected to represent
    a valid CURIE. A `ValueError` is raised otherwise.

    Extraction from the other types is infallible.

    Raises a `ValueError` if the `input` is not a `str`,
    a :class:`~hpotk.TermId`, or an :class:`~hpotk.model.Identified`.
    """
    if isinstance(input, str):
        return TermId.from_curie(input)
    elif isinstance(input, TermId):
        return input
    elif isinstance(input, Identified):
        return input.identifier
    else:
        raise ValueError(f"Unsupported input type {type(input)}")
