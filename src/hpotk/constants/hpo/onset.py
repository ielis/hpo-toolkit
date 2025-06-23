"""
A module with term IDs of the `Onset <https://hpo.jax.org/browse/term/HP:0003674>`_
sub-hierarchy of the HPO.
"""

from hpotk.model import TermId

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

#  #
MIDDLE_AGE_ONSET: TermId = TermId.from_curie("HP:0003596")
PERIMENOPAUSAL_ONSET: TermId = TermId.from_curie("HP:6000314")
POSTMENOPAUSAL_ONSET: TermId = TermId.from_curie("HP:6000315")
LATE_ONSET: TermId = TermId.from_curie("HP:0003584")


ALL_ONSETS = {
    ONSET, ANTENATAL_ONSET, EMBRYONAL_ONSET, FETAL_ONSET, LATE_FIRST_TRIMESTER_ONSET, SECOND_TRIMESTER_ONSET, THIRD_TRIMESTER_ONSET,
    CONGENITAL_ONSET, NEONATAL_ONSET, PUERPURAL_ONSET, PEDIATRIC_ONSET, INFANTILE_ONSET, CHILDHOOD_ONSET, JUVENILE_ONSET,
    ADULT_ONSET, YOUNG_ADULT_ONSET, EARLY_YOUNG_ADULT_ONSET, INTERMEDIATE_YOUNG_ADULT_ONSET, LATE_YOUNG_ADULT_ONSET,
    MIDDLE_AGE_ONSET, PERIMENOPAUSAL_ONSET, POSTMENOPAUSAL_ONSET, LATE_ONSET,
}
"""
A set of all members of the `Onset <https://hpo.jax.org/browse/term/HP:0003674>`_
HPO sub-hierarchy, including the root (`Onset`) term id.
"""
