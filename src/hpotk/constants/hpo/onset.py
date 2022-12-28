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
#  ##
MIDDLE_AGE_ONSET: TermId = TermId.from_curie("HP:0003596")
LATE_ONSET: TermId = TermId.from_curie("HP:0003584")
