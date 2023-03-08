import typing

from hpotk.model import Identified, TermId, CURIE_OR_TERM_ID


class HpoFrequency(Identified):

    def __init__(self, identifier: TermId,
                 lower_bound: float,
                 upper_bound: float):
        self._id = identifier
        self._lower = lower_bound
        self._upper = upper_bound

    @property
    def identifier(self) -> TermId:
        return self._id

    @property
    def lower_bound(self) -> float:
        return self._lower

    @property
    def upper_bound(self) -> float:
        return self._upper

    @property
    def frequency(self) -> float:
        return self._lower + self._upper / 2

    def __eq__(self, other):
        return isinstance(other, HpoFrequency) \
            and self._id == other._id \
            and self._lower == other._lower \
            and self._upper == other._upper

    def __str__(self):
        return f'HpoFrequency(identifier={self.identifier.value}, ' \
               f'lower_bound={self.lower_bound}, ' \
               f'upper_bound={self.upper_bound})'

    def __repr__(self):
        return str(self)


# Children of Frequency `HP:0040279`.
FREQUENCY: TermId = TermId.from_curie("HP:0040279")

EXCLUDED: TermId = TermId.from_curie("HP:0040285")
VERY_RARE: TermId = TermId.from_curie("HP:0040284")
OCCASIONAL: TermId = TermId.from_curie("HP:0040283")
FREQUENT: TermId = TermId.from_curie("HP:0040282")
VERY_FREQUENT: TermId = TermId.from_curie("HP:0040281")
OBLIGATE: TermId = TermId.from_curie("HP:0040280")


_frequencies = (
    HpoFrequency(EXCLUDED, 0., 0.),
    HpoFrequency(VERY_RARE, .01, .04),
    HpoFrequency(OCCASIONAL, .05, .29),
    HpoFrequency(FREQUENT, .3, .79),
    HpoFrequency(VERY_FREQUENT, .8, .99),
    HpoFrequency(OBLIGATE, 1., 1.)
)

HPO_FREQUENCIES = {fq.identifier: fq for fq in _frequencies}


def parse_hpo_frequency(value: CURIE_OR_TERM_ID) -> typing.Optional[HpoFrequency]:
    """
    Get :class:`HpoFrequency` for given HPO frequency term ID or `None` if the term ID does not represent
    a frequency term.

    :param value: a `str` or :class:`TermId` corresponding to HPO frequency term ID.
    :return: :class:`HpoFrequency` or `None`.
    """
    if isinstance(value, TermId):
        pass
    elif isinstance(value, str):
        value = TermId.from_curie(value)
    else:
        return None

    try:
        return HPO_FREQUENCIES[value]
    except KeyError:
        return None
