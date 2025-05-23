import typing

from hpotk.model import Identified, TermId, CURIE_OR_TERM_ID

class HpoOnset(Identified):

    def __init__(self, identifier: TermId):
        self._id = identifier

    @property
    def identifier(self) -> TermId:
        return self._id

    def __str__(self):
        return f'Onset(identifier={self.identifier.value}'

    def __repr__(self):
        return str(self)

#  Descendents of Onset `HP:0003674`. The `#`s model the hierarchy.
ONSET: TermId = TermId.from_curie("HP:0003674")

#  #
ANTENATAL_ONSET: TermId = TermId.from_curie("HP:0030674")
#  ##
EMBRYONAL_ONSET: TermId = TermId.from_curie("HP:0011460")
#  ##
FETAL_ONSET: TermId = TermId.from_curie("HP:0011461")
#  ###
LATE_FIRST_TRIMESTER_ONSET: TermId = TermId.from_curie("HP:0034199")
SECOND_TRIMESTER_ONSET: TermId = TermId.from_curie("HP:0034198")
THIRD_TRIMESTER_ONSET: TermId = TermId.from_curie("HP:0034197")

#  #
CONGENITAL_ONSET: TermId = TermId.from_curie("HP:0003577")
NEONATAL_ONSET: TermId = TermId.from_curie("HP:0003623")
PUERPURAL_ONSET: TermId = TermId.from_curie("HP:4000040")

#  #
PEDIATRIC_ONSET: TermId = TermId.from_curie("HP:0410280")
#  ##
INFANTILE_ONSET: TermId = TermId.from_curie("HP:0003593")
CHILDHOOD_ONSET: TermId = TermId.from_curie("HP:0011463")
JUVENILE_ONSET: TermId = TermId.from_curie("HP:0003621")

#  #
ADULT_ONSET: TermId = TermId.from_curie("HP:0003581")
#  ##
YOUNG_ADULT_ONSET: TermId = TermId.from_curie("HP:0011462")
#  ###
EARLY_YOUNG_ADULT_ONSET: TermId = TermId.from_curie("HP:0025708")
INTERMEDIATE_YOUNG_ADULT_ONSET: TermId = TermId.from_curie("HP:0025709")
LATE_YOUNG_ADULT_ONSET: TermId = TermId.from_curie("HP:0025710")
#  ##
MIDDLE_AGE_ONSET: TermId = TermId.from_curie("HP:0003596")
LATE_ONSET: TermId = TermId.from_curie("HP:0003584")

_onsets = (
    HpoOnset(ONSET),
    HpoOnset(ANTENATAL_ONSET),
    HpoOnset(EMBRYONAL_ONSET),
    HpoOnset(FETAL_ONSET),
    HpoOnset(LATE_FIRST_TRIMESTER_ONSET),
    HpoOnset(SECOND_TRIMESTER_ONSET),
    HpoOnset(THIRD_TRIMESTER_ONSET),
    HpoOnset(CONGENITAL_ONSET),
    HpoOnset(NEONATAL_ONSET),
    HpoOnset(PUERPURAL_ONSET),
    HpoOnset(PEDIATRIC_ONSET),
    HpoOnset(INFANTILE_ONSET),
    HpoOnset(CHILDHOOD_ONSET),
    HpoOnset(JUVENILE_ONSET),
    HpoOnset(ADULT_ONSET),
    HpoOnset(YOUNG_ADULT_ONSET),
    HpoOnset(EARLY_YOUNG_ADULT_ONSET),
    HpoOnset(INTERMEDIATE_YOUNG_ADULT_ONSET),
    HpoOnset(LATE_YOUNG_ADULT_ONSET),
    HpoOnset(MIDDLE_AGE_ONSET),
    HpoOnset(LATE_ONSET)
)

ONSETS = {onset.identifier: onset for onset in _onsets}

