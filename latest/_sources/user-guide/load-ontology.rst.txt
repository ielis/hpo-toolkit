.. _rstload-ontology:

=============
Load ontology
=============

Loading HPO is the first item of all analysis task lists.
HPO toolkit supports loading the ontology data from an `Obographs <https://github.com/geneontology/obographs>`_
JSON file which is available for download from the `HPO website <https://hpo.jax.org/app/data/ontology>`_.

Minimal ontology
^^^^^^^^^^^^^^^^

Let's load the HPO version released on Oct 9th, 2023:

.. doctest:: load-minimal-ontology

  >>> import hpotk

  >>> url = 'https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2023-10-09/hp.json'
  >>> hpo = hpotk.load_minimal_ontology(url)

The loader fetches the Obographs JSON file and loads the data into :class:`hpotk.ontology.MinimalOntology`.

.. note::

  The loader can fetch the HPO from a URL, and it transparently handles gzipped files
  if the file name ends with `.gz` suffix.

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
  >>> definition = seizure.definition
  >>> definition.definition
  'A seizure is an intermittent abnormality of nervous system physiology characterised by a transient occurrence of signs and/or symptoms due to abnormal excessive or synchronous neuronal activity in the brain.'
  >>> definition.xrefs
  ('https://orcid.org/0000-0002-0736-9199', 'PMID:15816939')


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

