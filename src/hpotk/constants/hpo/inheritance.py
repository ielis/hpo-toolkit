from hpotk.model import TermId

# Selected descendents of Mode of inheritance `HP:0000005`.

INHERITANCE_MODIFIER: TermId = TermId.from_curie("HP:0034335")
# Inheritance modifier descendents can be added if required.

#  ########################## Mendelian inheritance and its descendents #############################################  #
MENDELIAN_INHERITANCE: TermId = TermId.from_curie("HP:0034345")

PSEUDOAUTOSOMAL_INHERITANCE: TermId = TermId.from_curie("HP:0034339")
PSEUDOAUTOSOMAL_DOMINANT_INHERITANCE: TermId = TermId.from_curie("HP:0034340")
PSEUDOAUTOSOMAL_RECESSIVE_INHERITANCE: TermId = TermId.from_curie("HP:0034341")

X_LINKED_INHERITANCE: TermId = TermId.from_curie("HP:0001417")
X_LINKED_DOMINANT_INHERITANCE: TermId = TermId.from_curie("HP:0001423")
X_LINKED_RECESSIVE_INHERITANCE: TermId = TermId.from_curie("HP:0001419")


SEMIDOMINANT_INHERITANCE: TermId = TermId.from_curie("HP:0032113")
Y_LINKED_INHERITANCE: TermId = TermId.from_curie("HP:0001450")
AUTOSOMAL_DOMINANT_INHERITANCE: TermId = TermId.from_curie("HP:0000006")
AUTOSOMAL_RECESSIVE_INHERITANCE: TermId = TermId.from_curie("HP:0000007")
MITOCHONDRIAL_INHERITANCE: TermId = TermId.from_curie("HP:0001427")
#  ##################################################################################################################  #

#  ########################## Multifactorial inheritance and its descendents ########################################  #
MULTIFACTORIAL_INHERITANCE: TermId = TermId.from_curie("HP:0001426")
OLIGOGENIC_INHERITANCE: TermId = TermId.from_curie("HP:0010983")
POLYGENIC_INHERITANCE: TermId = TermId.from_curie("HP:0010982")
DIGENIC_INHERITANCE: TermId = TermId.from_curie("HP:0010984")
#  ##################################################################################################################  #

SPORADIC: TermId = TermId.from_curie("HP:0003745")
SOMATIC_MOSAICISM: TermId = TermId.from_curie("HP:0001442")
