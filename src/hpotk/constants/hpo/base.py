from hpotk.model import TermId

# Children of All `HP:0000001`, the root of the HPO hierarchy.

PHENOTYPIC_ABNORMALITY: TermId = TermId.from_curie('HP:0000118')
CLINICAL_MODIFIER: TermId = TermId.from_curie("HP:0012833")
MODE_OF_INHERITANCE: TermId = TermId.from_curie("HP:0000005")
PAST_MEDICAL_HISTORY: TermId = TermId.from_curie("HP:0032443")
BLOOD_GROUP: TermId = TermId.from_curie("HP:0032223")
FREQUENCY: TermId = TermId.from_curie("HP:0040279")
