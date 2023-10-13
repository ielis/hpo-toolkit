.. _rstload-ontology:

=============
Load ontology
=============

Loading HPO is the first item of all analysis task lists.
HPO toolkit supports loading the ontology data from an `Obographs <https://github.com/geneontology/obographs>`_
JSON file which is available for download from the `HPO website <https://hpo.jax.org/app/data/ontology>`_.

Minimal ontology
^^^^^^^^^^^^^^^^

Let's load HPO:

.. doctest:: load-minimal-ontology

  >>> import hpotk

  >>> hpo = hpotk.load_minimal_ontology('data/hp.toy.json')
  >>> hpo.version
  '2022-10-05'

We load the ontology from a toy Obographs JSON file and we check the version of the data.

.. note::

  The loader can fetch the HPO from a URL, and it transparently handles gzipped files
  if the file name ends with `.gz` suffix.

Now, we can check that the toy HPO has 393 primary terms:

.. doctest:: load-minimal-ontology

  >>> len(hpo)
  393

check that `HP:0001250` is/was a valid identifier:

.. doctest:: load-minimal-ontology

  >>> 'HP:0001250' in hpo
  True

check that `HP:0001250` in fact represents *Seizure*:

.. doctest:: load-minimal-ontology

  >>> seizure = hpo.get_term('HP:0001250')
  >>> seizure.name
  'Seizure'

or print names of its children in alphabetical order:

.. doctest:: load-minimal-ontology

  >>> children_names = sorted(
  ...                    map(lambda ch: hpo.get_term(ch).name,
  ...                      hpo.graph.get_children(seizure)))
  >>> for child in children_names:
  ...   print(child)
  Focal-onset seizure
  Motor seizure

.. note::

  The toy HPO is a subset of the full HPO and Seizure only 2 child terms in the toy file. There are more children
  in the real-life ("production") HPO.

The terms of :class:`hpotk.ontology.MinimalOntology` are instances of :class:`hpotk.model.MinimalTerm` and contain a subset
of the term metadata such as identifier, labels, and alternative IDs. The simplified are useful for tasks that
use the ontology hierarchy. However, the tasks that need the full term metadata should use `Ontology`.

Ontology
^^^^^^^^

Unsurprisingly, loading ontology is very similar to loading minimal ontology. We use `hpotk.load_ontology`
loader function:

.. testsetup:: load-ontology

  import hpotk

.. doctest:: load-ontology

  >>> hpo = hpotk.load_ontology('data/hp.toy.json')
  >>> hpo.version
  '2022-10-05'

Same as above, the loader parses the Obographs JSON file and returns an ontology. However, this time
it is an instance :class:`hpotk.ontology.Ontology` with :class:`hpotk.model.Term` - the term with full metadata.

So, now we can access the definition of the seizure:

.. doctest:: load-ontology

  >>> seizure = hpo.get_term('HP:0001250')
  >>> seizure.definition
  'A seizure is an intermittent abnormality of nervous system physiology characterised by a transient occurrence of signs and/or symptoms due to abnormal excessive or synchronous neuronal activity in the brain.'

or check out seizure's synonyms:

.. doctest:: load-ontology

  >>> for synonym in seizure.synonyms:
  ...   print(synonym.name)
  Seizures
  Epilepsy
  Epileptic seizure

.. note::

  Since `Ontology` is a subclass of `MinimalOntology`, any function that needs `MinimalOntology` will work just fine
  when provided with `Ontology`.

