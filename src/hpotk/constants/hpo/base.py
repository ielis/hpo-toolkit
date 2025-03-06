from hpotk.model import TermId

# Children of All `HP:0000001`, the root of the HPO hierarchy.

PHENOTYPIC_ABNORMALITY: TermId = TermId.from_curie('HP:0000118')
"""
Phenotypic abnormality is the parent term of all phenotypic features of HPO.
"""

CLINICAL_MODIFIER: TermId = TermId.from_curie("HP:0012833")
"""
Clinical modifier is the parent term of the clinical modifier HPO module.
"""

MODE_OF_INHERITANCE: TermId = TermId.from_curie("HP:0000005")
"""
Mode of inheritance is the parent term of the inheritance mode subgraph.
"""

ONSET: TermId = TermId.from_curie("HP:0003674")
"""
Onset is the parent term of the onset mode subgraph.
"""

PAST_MEDICAL_HISTORY: TermId = TermId.from_curie("HP:0032443")
BLOOD_GROUP: TermId = TermId.from_curie("HP:0032223")
FREQUENCY: TermId = TermId.from_curie("HP:0040279")
