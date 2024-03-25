.. _sort-term-ids:

================
Sorting term IDs
================

Working with HPO typically includes working with items (e.g. patients) annotated with HPO terms.
However, the annotations are rarely sorted in any meaningful order which can obscure the interpretation.
HPO toolkit provides logic for sorting HPO terms such that the similar terms are located closer than the rest.

Let's illustrate this on example. Suppose having a subject annotated with the following terms:

>>> import hpotk
>>> subject = (
...   'HP:0001744',  # Splenomegaly
...   'HP:0020221',  # Clonic seizure
...   'HP:0001238',  # Slender finger
...   'HP:0011153',  # Focal motor seizure
...   'HP:0002240'   # Hepatomegaly
... )
>>> term_ids = tuple(hpotk.TermId.from_curie(curie) for curie in subject)


The order of HPO annotations does not reflect that *Splenomegaly* is more "similar" to *Hepatomegaly* than
to *Clonic seizure*. The implementations of :class:`hpotk.util.sort.TermIdSorting` endeavor to improve on this.

The sorting logic is handled by :class:`hpotk.util.sort.TermIdSorting` implementations. The algorithm takes
a sequence of term IDs or :class:`hpotk.model.Identified` entities, such as :class:`hpotk.model.Term`, and returns
indices for sorting the input sequence - the same what :func:`numpy.argsort` does.


Hierarchical sorting
^^^^^^^^^^^^^^^^^^^^

:class:`hpotk.util.sort.HierarchicalEdgeTermIdSorting` sorts the term IDs using a combination of hierarchical
clustering and `graph edge distance <https://en.wikipedia.org/wiki/Distance_(graph_theory)>`_.
The algorithm iteratively chooses the most similar term ID pairs and places them into adjacent locations.

We'll use a toy HPO with several terms to present the functionality:

>>> import os
>>> fpath_hpo = os.path.join('docs', 'data', 'hp.toy.json')
>>> hpo = hpotk.load_minimal_ontology(fpath_hpo)

>>> from hpotk.util.sort import HierarchicalEdgeTermIdSorting
>>> sorting = HierarchicalEdgeTermIdSorting(hpo)

We can obtain the indices that will sort the HPO terms and prepare a `tuple` with sorted terms:


>>> indices = sorting.argsort(term_ids)
>>> ordered = tuple(term_ids[idx] for idx in indices)

Now let's look at the order. Originally, the HPO terms were ordered as follows::

  'HP:0001744'   # Splenomegaly
  'HP:0020221'   # Clonic seizure
  'HP:0001238'   # Slender finger
  'HP:0011153'   # Focal motor seizure
  'HP:0002240'   # Hepatomegaly

After the sorting, we get this order:


>>> for term_id in ordered:
...   print(hpo.get_term(term_id).name)
Focal motor seizure
Clonic seizure
Hepatomegaly
Splenomegaly
Slender finger

which is much better, right?
