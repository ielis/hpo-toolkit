.. _load-hpo-annotations:

===============
HPO annotations
===============

The HPO projects offers phenotype annotations to describe the connection between diseases and HPO terms.
The annotations are available for download from `HPO annotation release <https://hpo.jax.org/app/data/annotations>`_
site in tabular format.


Load HPO annotations
^^^^^^^^^^^^^^^^^^^^

HPO toolkit provides means to parse and work with the disease models
and here we show how to load the HPO annotation file.

The loader needs HPO to Q/C the annotations, hence we must load HPO first. We need the HPO version corresponding
to the annotations version, although a more recent HPO version should generally work as well.

.. doctest:: hpoa-io

  >>> import hpotk

  >>> base_url = 'https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2023-10-09/'
  >>> hpo = hpotk.load_minimal_ontology(base_url + 'hp.json')

Now, we can load a the annotation file.

.. doctest:: hpoa-io

  >>> from hpotk.annotations.load.hpoa import SimpleHpoaDiseaseLoader

  >>> loader = SimpleHpoaDiseaseLoader(hpo)
  >>> diseases = loader.load(base_url + 'phenotype.hpoa')
  >>> diseases.version
  '2023-10-09'
  >>> len(diseases)
  12468

We loaded `diseases`, an instance of :class:`hpotk.annotations.HpoDiseases` with `12468` disease models.

Now, we can iterate over all diseases:

.. doctest:: hpoa-io

  >>> sum(1 for disease in diseases)
  12468

or we can get a disease for a given identifier:

.. doctest:: hpoa-io

  >>> disease = diseases['OMIM:256000']
  >>> disease.name
  'Leigh syndrome'

The identifier can be a CURIE `str` (above) or a :class:`hpotk.model.TermId`:

.. doctest:: hpoa-io

  >>> disease = diseases[hpotk.TermId.from_curie('OMIM:256000')]
  >>> disease.name
  'Leigh syndrome'


Disease model
^^^^^^^^^^^^^

HPO toolkit provides :class:`hpotk.annotations.HpoDisease` to model the disease data. `HpoDisease` is a simple
data class with a limited functionality on top of just providing the data. Let's check out the available attributes.

We can access the identifier and name of the disease:

.. doctest:: hpoa-io

  >>> str(disease.identifier)
  'OMIM:256000'
  >>> disease.name
  'Leigh syndrome'

We can access the phenotype annotations of the disease. In case of `Leigh disease` there are `30` annotations:

.. doctest:: hpoa-io

  >>> len(disease.annotations)
  30

Let's examine the first annotation in greater detail:

.. doctest:: hpoa-io

  >>> a = next(iter(disease.annotations))
  >>> str(a.identifier)
  'HP:0000486'
  >>> hpo.get_term_name(a)
  'Strabismus'

.. seealso::

  See :class:`hpotk.annotations.HpoDiseaseAnnotation` for more details on the phenotype annotations.

We can also access the modes of inheritance:

.. doctest:: hpoa-io

  >>> for moi in sorted(disease.modes_of_inheritance):
  ...   print(moi, hpo.get_term_name(moi))
  HP:0000007 Autosomal recessive inheritance
  HP:0001427 Mitochondrial inheritance
