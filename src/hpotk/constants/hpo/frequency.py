from hpotk.model import TermId

# Children of Frequency `HP:0040279`.
FREQUENCY: TermId = TermId.from_curie("HP:0040279")

EXCLUDED: TermId = TermId.from_curie("HP:0040285")
VERY_RARE: TermId = TermId.from_curie("HP:0040284")
OCCASIONAL: TermId = TermId.from_curie("HP:0040283")
FREQUENT: TermId = TermId.from_curie("HP:0040282")
VERY_FREQUENT: TermId = TermId.from_curie("HP:0040281")
OBLIGATE: TermId = TermId.from_curie("HP:0040280")
