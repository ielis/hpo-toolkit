.. _sort-term-ids:

================
Sorting term IDs
================

Working with HPO typically includes working with items (e.g. patients) annotated with HPO terms.
However, the annotations are rarely sorted in any meaningful order which can obscure the interpretation.
HPO toolkit provides logic for sorting HPO terms such that the similar terms are located closer than the rest.

Let's illustrate this on example. Suppose having a subject annotated with the following terms:

.. doctest:: sort-term-ids

  >>> subject = (
  ...   'HP:0001744',  # Splenomegaly
  ...   'HP:0020221',  # Clonic seizure
  ...   'HP:0001238',  # Slender finger
  ...   'HP:0011153',  # Focal motor seizure
  ...   'HP:0002240'   # Hepatomegaly
  ... )
  >>> term_ids = tuple(TermId.from_curie(curie) for curie in subject)


The order of HPO annotations does not reflect that *Splenomegaly* is more "similar" to *Hepatomegaly* than
to *Clonic seizure*. The implementations of :class:`hpotk.util.sort.TermIdSorting` endeavor to improve on this.

The sorting logic is handled by :class:`hpotk.util.sort.TermIdSorting` implementations. The algorithm takes
a sequence of term IDs or :class:`hpotk.model.Identified` entities, such as :class:`hpotk.model.Term`, and returns
indices for sorting the input sequence - the same what :func:`numpy.argsort` does.


Hierarchical sorting
^^^^^^^^^^^^^^^^^^^^

:class:`hpotk.util.sort.HierarchicalSimilaritySorting` sorts the term IDs using a combination of hierarchical
clustering and Resnik semantic similarity. The algorithm iteratively chooses the most similar term ID pairs
and places them into adjacent locations.

The sorting needs HPO graph and a callable for getting an information content (IC) of an ontology term.
We'll use a toy HPO with several terms and information content of terms prepared using
:func:`hpotk.algorithm.similarity.calculate_ic_for_annotated_items`:

.. doctest:: sort-term-ids

  >>> hpo = hpotk.ontology.load.obographs.load_minimal_ontology('data/hp.toy.json')

  >>> import json
  >>> with open('data/hp.toy.ic.json') as fh:
  ...   ic_dict = json.load(fh)
  >>> ic_dict = {TermId.from_curie(curie): ic for curie, ic in ic_dict.items()}

  >>> def ic_source(term_id: TermId) -> float:
  ...   return ic_dict.get(term_id, 0.)

Now we can instantiate `HierarchicalSimilaritySorting`:

.. doctest:: sort-term-ids

  >>> from hpotk.util.sort import HierarchicalSimilaritySorting

  >>> sorting = HierarchicalSimilaritySorting(hpo, ic_source)

And sort the HPO terms:

.. doctest:: sort-term-ids

  >>> indices = sorting.argsort(term_ids)
  >>> ordered = tuple(term_ids[idx] for idx in indices)

Now let's look at the order:

.. doctest:: sort-term-ids

  >>> for term_id in ordered:
  ...   print(hpo.get_term(term_id).name)
  Hepatomegaly
  Splenomegaly
  Focal motor seizure
  Clonic seizure
  Slender finger

which is much better, right?
