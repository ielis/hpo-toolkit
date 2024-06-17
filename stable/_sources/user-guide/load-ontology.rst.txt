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

Loading other ontologies
************************

HPO toolkit primarily supports HPO, but few other ontologies were tested as an experimental feature.

HPO toolkit should load Medical Action Ontology (MAxO) and Mondo Disease Ontology (MONDO).
For instance:

.. doctest:: load-minimal-ontology

  >>> url = 'https://github.com/monarch-initiative/MAxO/releases/download/v2024-05-24/maxo.json'
  >>> maxo = hpotk.load_minimal_ontology(url, prefixes_of_interest={'MAXO'})
  >>> maxo.version
  '2024-05-24'

We provided `prefixes_of_interest` option to limit the terms to those with `MAXO` prefix, 
effectively discarding all terms of other ontologies from the loading process. In result,
the ontology includes only the `MAXO` terms along with the corresponding ontology graph.

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
in the tag section of the `HPO release page <https://github.com/obophenotype/human-phenotype-ontology/tags>`_.

Moreover, `OntologyStore` will load the *latest* release, if the `release` option is omitted.

.. doctest:: load-minimal-ontology

  >>> hpo_latest = store.load_minimal_hpo()  # doctest: +SKIP
  >>> hpo_latest.version  # doctest: +SKIP
  '2024-03-06'

As of the time of this writing, ``2024-03-06`` is the latest HPO release.


The store exposes the path of the ontology resources. For HPO, this is the path to the JSON file:

.. doctest:: load-minimal-ontology

  >>> fpath_hpo = store.resolve_store_path(ontology_type=hpotk.OntologyType.HPO, release='v2023-10-09')
  >>> fpath_hpo  # doctest: +SKIP
  '/path/to/.hpo-toolkit/HP/hp.v2023-10-09.json'

The ontology resources can be cleaned to remove the content of the local directory:

.. doctest:: load-minimal-ontology

  >>> store.clear()  # doctest: +SKIP


Support for other ontologies
****************************

HPO toolkit was developed to work best with HPO, since it is the flagship ontology of the toolkit's developers. 
However, support for loading of several other ontologies was tested as an experimental feature:

* Medical Action Ontology (MAxO)
  * `Manuscript <https://pubmed.ncbi.nlm.nih.gov/37963467>`_
  * `GitHub <https://github.com/monarch-initiative/MAxO>`_
* Mondo Disease Ontology (MONDO)
  * `Website <https://mondo.monarchinitiative.org>`_
  * `GitHub <https://github.com/monarch-initiative/mondo>`_

Let's start with loading MAxO:

.. doctest:: load-minimal-ontology

  >>> maxo = store.load_minimal_ontology(
  ...     hpotk.store.OntologyType.MAxO, release="v2024-05-24",
  ...     prefixes_of_interest={'MAXO'},
  ... )

Note that we added the `prefixes_of_interest` option - a `set` of term prefixes that should be kept 
when loading the ontology file.

Mondo is loaded in a very similar fashion:

.. doctest:: load-minimal-ontology

  >>> mondo = store.load_minimal_ontology(
  ...     hpotk.OntologyType.MONDO, release='v2024-06-04',
  ...     prefixes_of_interest={'MONDO',},
  ... )

Note, this guide shows the loading with a set versions. 
However, other versions are supported as long as an existing release tag is used.
Check the ontology releases for the available tags.


Next steps
**********

Loading an ontology is a prerequisite for doing anything useful with the ontology data. Check out
the :ref:`use-ontology` section for an overview of the functionality.
