from hpotk.model import TermId

# Selected descendents of Mode of inheritance `HP:0000005`.

INHERITANCE_MODIFIER: TermId = TermId.from_curie("HP:0034335")
# Inheritance modifier descendents can be added if required.

#  ########################## Mendelian inheritance and its descendents #############################################  #
MENDELIAN_INHERITANCE: TermId = TermId.from_curie("HP:0034345")
"""
HP:0034345 | A mode of inheritance of diseases whose pathophysiology can be traced back to deleterious variants in a single gene.
The inheritance patterns of these single-gene (monogenic) diseases are often referred to as Mendelian in honor of Gregor Mendel. 
"""

PSEUDOAUTOSOMAL_INHERITANCE: TermId = TermId.from_curie("HP:0034339")
PSEUDOAUTOSOMAL_DOMINANT_INHERITANCE: TermId = TermId.from_curie("HP:0034340")
PSEUDOAUTOSOMAL_RECESSIVE_INHERITANCE: TermId = TermId.from_curie("HP:0034341")

X_LINKED_INHERITANCE: TermId = TermId.from_curie("HP:0001417")
X_LINKED_DOMINANT_INHERITANCE: TermId = TermId.from_curie("HP:0001423")
X_LINKED_RECESSIVE_INHERITANCE: TermId = TermId.from_curie("HP:0001419")


SEMIDOMINANT_INHERITANCE: TermId = TermId.from_curie("HP:0032113")
Y_LINKED_INHERITANCE: TermId = TermId.from_curie("HP:0001450")
AUTOSOMAL_DOMINANT_INHERITANCE: TermId = TermId.from_curie("HP:0000006")
"""
`HP:0000006` | A mode of inheritance that is observed for traits related to a gene encoded on one of the autosomes (i.e., the human chromosomes 1-22)
in which a trait manifests in heterozygotes.

In the context of medical genetics, an autosomal dominant disorder is caused when a single copy of the mutant allele is present.
Males and females are affected equally, and can both transmit the disorder with a risk of 50% for each child of inheriting the mutant allele.
"""

AUTOSOMAL_RECESSIVE_INHERITANCE: TermId = TermId.from_curie("HP:0000007")
"""
`HP:0000007` | A mode of inheritance that is observed for traits related to a gene encoded on one of the autosomes (i.e., the human chromosomes 1-22)
in which a trait manifests in individuals with two pathogenic alleles, either homozygotes (two copies of the same mutant allele)
or compound heterozygotes (whereby each copy of a gene has a distinct mutant allele). 
"""

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
