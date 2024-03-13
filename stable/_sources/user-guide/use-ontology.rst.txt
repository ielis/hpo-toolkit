.. _use-ontology:

============
Use ontology
============

HPO toolkit simplifies working with Human Phenotype Ontology from Python by providing APIs
for accessing the ontology data. Here we show how to access the data.

  We assume the reader is familiar with loading ontology from an Obographs JSON file as described
  in the :ref:`rstload-ontology` section.

HPO toolkit represents the ontology data either as :class:`hpotk.ontology.MinimalOntology`
or as its subclass :class:`hpotk.ontology.Ontology`.
The two classes are mostly equivalent but the `MinimalOntology` terms contain less metadata than the `Ontology` terms.
We recommend using `MinimalOntology` for applications that mostly care about the ontology hierarchy and
`Ontology` is suitable for applications that use definitions, synonyms, or cross-references of the ontology terms,
such as natural language processing applications.


Minimal ontology
^^^^^^^^^^^^^^^^

Let's see what we can do with a `MinimalOntology`.

We start with loading the version `v2023-10-09` using :class:`hpotk.util.store.OntologyStore`:

.. doctest:: load-minimal-ontology

  >>> import hpotk
  >>> store = hpotk.configure_ontology_store()

  >>> hpo = store.load_minimal_hpo(release='v2023-10-09')

We can check the HPO version:

.. doctest:: load-minimal-ontology

  >>> hpo.version
  '2023-10-09'

check that the release has *17,664* terms:

.. doctest:: load-minimal-ontology

  >>> len(hpo)
  17664

check that `HP:0001250` is/was a valid term id:

.. doctest:: load-minimal-ontology

  >>> 'HP:0001250' in hpo
  True

check that `HP:0001250` in fact represents *Seizure*:

.. doctest:: load-minimal-ontology

  >>> seizure = hpo.get_term('HP:0001250')
  >>> seizure.name
  'Seizure'

or print the names of its children in alphabetical order:

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
use the ontology hierarchy.

Ontology
^^^^^^^^

Unsurprisingly, loading ontology is very similar to loading minimal ontology. Same as above,
we use :class:`hpotk.util.store.OntologyStore`:

.. doctest:: load-ontology

  >>> import hpotk
  >>> store = hpotk.configure_ontology_store()

  >>> hpo = store.load_hpo(release='v2023-10-09')
  >>> hpo.version
  '2023-10-09'

Same as above, the ontology store will check the local cache for the ontology data file of the requested release
and fetch the file from HPO release page if missing. Then, the file is parsed into :class:`hpotk.ontology.Ontology`,
where the ontology terms are represented as :class:`hpotk.model.Term`.

Thanks to the additional metadata present in a `Term`, we can also access the definition of the *Seizure*:

.. doctest:: load-ontology

  >>> seizure = hpo.get_term('HP:0001250')
  >>> definition = seizure.definition
  >>> definition.definition
  'A seizure is an intermittent abnormality of nervous system physiology characterised by a transient occurrence of signs and/or symptoms due to abnormal excessive or synchronous neuronal activity in the brain.'
  >>> definition.xrefs
  ('https://orcid.org/0000-0002-0736-9199', 'PMID:15816939')

or its synonyms:

.. doctest:: load-ontology

  >>> for synonym in seizure.synonyms:
  ...   print(synonym.name)
  Epileptic seizure
  Seizures
  Epilepsy

.. note::

  Since `Ontology` is a subclass of `MinimalOntology`, any function that needs `MinimalOntology` will work just fine
  when provided with `Ontology`.

