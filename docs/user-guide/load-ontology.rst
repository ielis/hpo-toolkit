.. _rstload-ontology:

=============
Load ontology
=============

Loading HPO is the first item of all analysis task lists.
HPO toolkit supports loading the ontology data from an `Obographs <https://github.com/geneontology/obographs>`_
JSON file which is available for download from the `HPO website <https://hpo.jax.org/app/data/ontology>`_.

Ontology loaders
****************

HPO toolkit provides 2 ways for loading an ontology: a low-level loader and a high-level :class:`OntologyStore`.

Low level loader
^^^^^^^^^^^^^^^^

The low-level loader function loads a :class:`hpotk.ontology.MinimalOntology` from a local or remote resource.
The loader will open the resource and parse its contents into an ontology. Any failure is reported as an exception.

Let's load the HPO version released on Oct 9th, 2023:

.. doctest:: load-minimal-ontology

  >>> import hpotk

  >>> url = 'https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2023-10-09/hp.json'
  >>> hpo = hpotk.load_minimal_ontology(url)
  >>> hpo.version
  '2023-10-09'

We use the :func:`hpotk.ontology.load.obographs.load_minimal_ontology` function to fetch the Obographs JSON file
and to load the data into :class:`hpotk.ontology.MinimalOntology`.

.. note::

  The loader can fetch the HPO from a local path (relative or absolute), or from a URL,
  and it transparently handles decompression of gzipped files if the file name has a `.gz` suffix.

A similar loader function :func:`hpotk.ontology.load.obographs.load_ontology` exists
to load an :class:`hpotk.ontology.Ontology`.


Ontology store
^^^^^^^^^^^^^^

Alternatively, we can use the :class:`hpotk.util.store.OntologyStore`, a class that wraps the low-level loader
and provides more convenience.

Using `OntologyStore` provides several benefits. `OntologyStore` caches the ontology data files in a local directory
to prevent downloading a HPO release more than once, to save time spent during slow network access.

.. doctest:: load-minimal-ontology

  >>> store = hpotk.configure_ontology_store()
  >>> hpo = store.load_minimal_hpo(release='v2023-10-09')
  >>> hpo.version
  '2023-10-09'

The store will download the ontology file the first time a release (e.g. `v2023-10-09`) is requested, and subsequent
loads will skip the download. The `release` must be a release tag, as defined
on `HPO release page<https://github.com/obophenotype/human-phenotype-ontology/releases>`_.

Moreover, `OntologyStore` can get you a latest release by *not* specifying the `release` option.

.. doctest:: load-minimal-ontology

  >>> hpo_latest = store.load_minimal_hpo()  # doctest: +SKIP
  >>> hpo_latest.version  # doctest: +SKIP
  '2024-03-06'

As of the time of this writing, ``2024-03-06`` is the latest HPO release.


Quick overview
**************

Here we provide a quick walkthrough of the basic functionality of an ontology.

Minimal ontology
^^^^^^^^^^^^^^^^

Having `MinimalOntology`, we can do several checks. We can check the HPO version:

.. doctest:: load-minimal-ontology

  >>> hpo.version
  '2023-10-09'

check that the Oct 9th release has *17,664* terms:

.. doctest:: load-minimal-ontology

  >>> len(hpo)
  17664

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

  >>> for child in sorted(hpo.get_term_name(child)
  ...                     for child in hpo.graph.get_children(seizure)):
  ...   print(child)
  Bilateral tonic-clonic seizure
  Dialeptic seizure
  Focal-onset seizure
  Generalized-onset seizure
  Infection-related seizure
  Maternal seizure
  Motor seizure
  Neonatal seizure
  Nocturnal seizures
  Non-motor seizure
  Reflex seizure
  Status epilepticus
  Symptomatic seizures

The terms of :class:`hpotk.ontology.MinimalOntology` are instances of :class:`hpotk.model.MinimalTerm` and contain a subset
of the term metadata such as identifier, labels, and alternative IDs. The simplified are useful for tasks that
use the ontology hierarchy. However, the tasks that need the full term metadata should use `Ontology`.

Ontology
^^^^^^^^

Unsurprisingly, loading ontology is very similar to loading minimal ontology. We use `hpotk.load_ontology`
loader function:

.. testsetup:: load-ontology

  import hpotk
  url = 'https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2023-10-09/hp.json'

.. doctest:: load-ontology

  >>> hpo = hpotk.load_ontology(url)
  >>> hpo.version
  '2023-10-09'

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
  Epileptic seizure
  Seizures
  Epilepsy

.. note::

  Since `Ontology` is a subclass of `MinimalOntology`, any function that needs `MinimalOntology` will work just fine
  when provided with `Ontology`.

