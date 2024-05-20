.. _traverse-hierarchy:

======================
Use ontology hierarchy
======================

As a refresher, the ontology is a terminology that consists of a list of standardized concepts of a domain
along with semantic relationships between the domain concepts. We can model the ontology using a graph data structure
that consists of nodes (concepts/terms) and edges (relationships). HPO toolkit does not currently attempt
to model the entire complexity of ontologies (e.g all kinds of relationship types) and instead focuses solely
on a single relationship type: `"is_a"` to represent the concept hierarchy.

HPO toolkit enables accessing the ontology hierarchy through the :class:`hpotk.graph.OntologyGraph` API which is
in turn available through :class:`hpotk.ontology.MinimalOntology`. In other words, each ontology has the ontology graph
as a property:

>>> import os
>>> import hpotk

>>> fpath_hpo = os.path.join('docs', 'data', 'hp.toy.json')
>>> hpo = hpotk.load_minimal_ontology(fpath_hpo)
>>> hpo.graph
CsrIndexedOntologyGraph(root=HP:0000001, n_nodes=393)


We can leverage the hierarchy to infer a lot of extra information about the concepts, and, for instance,
empower fuzzy searches. The applications usually use lower-level routines that perform ontology graph traversals
and that's what we'll cover in this tutorial.

Hierarchy traversals
^^^^^^^^^^^^^^^^^^^^

In contrast with the typical graph lingo where the traversal involves finding successors and predecessors of a node,
the `OntologyGraph` uses simpler language and talks about the traversal in terms of children and parent nodes
of a term. The API provides methods for accessing parents/children (or in general ancestors/descendants) of
a term instead of successor/predecessors of a node. Let's illustrate this on a couple of examples.

We can get term IDs of the *parents* of a term, such as `Seizure <https://hpo.jax.org/app/browse/term/HP:0001250>`_
[`HP:0001250`] by calling:

>>> for parent in hpo.graph.get_parents('HP:0001250'):
...   print(parent)
HP:0012638

`HP:0012638` corresponds to
`Abnormal nervous system physiology <https://hpo.jax.org/app/browse/term/HP:0012638>`_.

*Children* are accessed in a similar fashion:

>>> for child in hpo.graph.get_children('HP:0001250'):
...   print(child)
HP:0020219
HP:0007359


We will leave finding the ancestors or descendants of a term as an exercise for the interested reader.

Hierarchy-based tests
^^^^^^^^^^^^^^^^^^^^^

`OntologyGraph` wraps the ancestor/descendant accessors in a convenience methods for testing if two terms are
ancestors/descendants of each other.

We can test if Seizure [`HP:0001250`] is a parent or an ancestor of Clonic seizure [`HP:0020221`]:

>>> hpo.graph.is_parent_of('HP:0001250', 'HP:0020221')
False

>>> hpo.graph.is_ancestor_of('HP:0001250', 'HP:0020221')
True

Similar methods exist for checking if a term is a child or a descendant of another term.


Augmenting term with ancestors/descendants
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO - show ancestors/descendants with `include_source`.

.. _iterable-vs-iterator:

Iterators vs. collections
^^^^^^^^^^^^^^^^^^^^^^^^^

You may have noticed the looping in the previous examples. The API does *not* promise a `set`, `list`, or any
other collection and it provides :class:`typing.Iterator` instead.
Therefore, the ontology graph implementation may choose to return a lazily evaluated iterable implementation.

The iterators have pros and cons. Thanks to the lazy evaluation, we do not need to calculate the entire
ancestor/descendant set if all we need is to find one of the terms.
On the flip side, we need to *"collect"* the iterator into a list/set if that's what we're really after,
incurring unnecessary creation of a new collection.

.. TODO - move tutorial parts here.
