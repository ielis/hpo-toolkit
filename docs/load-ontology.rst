.. _rstload-ontology:

=============
Load ontology
=============

Loading the ontology data is probably the single most common task prior any downstream analysis. HPO toolkit currently
supports loading the ontology data from an `Obographs <https://github.com/geneontology/obographs>`_ JSON file.
The toolkit provides convenience functions for loading the ontology.

Ontology vs. minimal ontology
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

However, before jumping to the loading process, we should briefly mention the difference between
:class:`hpotk.ontology.MinimalOntology` and :class:`hpotk.ontology.Ontology`. Simply put, the ontology keeps around
full metadata of the ontology concepts, while the minimal ontology. Therefore, as a rule of thumb, `MinimalOntology`
should be used in analyses that mostly use the ontology hierarchy, while `Ontology` is preferred for accessing term
synonyms, cross-references, or term authors and external references. `MinimalOntology` uses less RAM and loading
is slightly faster.

.. note::

  Since `Ontology` is a subclass of `MinimalOntology`, any function that needs `MinimalOntology` will work just fine
  when provided with `Ontology`.

Load minimal ontology
^^^^^^^^^^^^^^^^^^^^^

Let's load `MinimalOntology` from a toy HPO JSON file:

.. doctest:: load-minimal-ontology

  >>> import hpotk

  >>> toy_hpo_path = 'data/hp.toy.json'
  >>> hpo = hpotk.ontology.load.obographs.load_minimal_ontology(toy_hpo_path)

The loading takes a few seconds. Note, the loader can fetch the HPO from a URL, and transparently handles gzipped
files if the file name ends with `.gz`.

Now we can check that the toy HPO has 393 primary terms:

.. doctest:: load-minimal-ontology

  >>> len(hpo)
  393

check that `HP:0001250` is/was a valid identifier:

.. doctest:: load-minimal-ontology

  >>> 'HP:0001250' in hpo
  True

check that `HP:0001250` in fact represents *Seizure`:

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

Load ontology
^^^^^^^^^^^^^

Loading `Ontology` is unsurprisingly similar to loading its minimal companion. The only difference is in
the loader function:

.. testsetup:: load-ontology

  import hpotk
  toy_hpo_path = 'data/hp.toy.json'

.. doctest:: load-ontology

  >>> hpo = hpotk.ontology.load.obographs.load_ontology(toy_hpo_path)

Same as above, the loader parses the Obographs JSON file and returns an ontology. However, this time
it is :class:`hpotk.ontology.Ontology` - an ontology with richer ontology concept metadata.

So, we can access the definition of the term:

.. doctest:: load-ontology

  >>> seizure = hpo.get_term('HP:0001250')
  >>> seizure.definition
  'A seizure is an intermittent abnormality of nervous system physiology characterised by a transient occurrence of signs and/or symptoms due to abnormal excessive or synchronous neuronal activity in the brain.'

Check out the synonyms:

.. doctest:: load-ontology

  >>> for synonym in seizure.synonyms:
  ...   print(synonym.name)
  Seizures
  Epilepsy
  Epileptic seizure

