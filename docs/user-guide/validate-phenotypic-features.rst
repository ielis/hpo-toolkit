.. _validate-phenotypic-features:

============================
Validate phenotypic features
============================

One of the most convenient benefits of using ontology concepts for annotation of items with features and properties
is that one can leverage the information encoded in the semantic relationships of the ontology hierarchy.
Among other things, the semantic relationships empower fuzzy searches and similarity measures that have found
broad usage in many fields, such as biomedicine.

HPO became a *de facto* standard for representing phenotypic features - the signs and symptoms of an individual.
However, unlike in the case of other ontologies, several unique rules should be followed to maximize the benefits
of HPO annotations. In the sections below, we describe the rules and show how HPO toolkit can reveal their violations.

For the sake of this guide, let's assume we have an individual annotated with the following four phenotypic features:

* *Arachnodactyly*
* *Seizure*
* *Focal clonic seizure*
* *Enuresis nocturna*

.. doctest:: check-consistency

  >>> curies = [
  ...   'HP:0001505',  # Arachnodactyly
  ...   'HP:0001250',  # Seizure
  ...   'HP:0002266',  # Focal clonic seizure
  ...   'HP:0010677'   # Enuresis nocturna
  ... ]

Let's convert the CURIEs into term ids:

.. doctest:: check-consistency

  >>> import hpotk
  >>> term_ids = [hpotk.TermId.from_curie(curie) for curie in curies]

and let's finish the setup by loading the toy HPO shipped with the documentation.

.. doctest:: check-consistency

  >>> hpo = hpotk.load_minimal_ontology('data/hp.toy.json')


Do not use obsolete term ids
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As the first rule, the annotations should always use the current identifier. During ontology development,
some concepts may become obsolete and later be removed from the ontology altogether.
Most of the time, however, the removed concepts have a straightforward replacement.

The :class:`hpotk.validate.ObsoleteTermIdsValidator` points out the usage of obsolete term ids
and suggests the replacement.

Let's create the validator and check if the phenotypic features are OK:

.. doctest:: check-consistency

  >>> from hpotk.validate import ObsoleteTermIdsValidator
  >>> obs_val = ObsoleteTermIdsValidator(hpo)

  >>> vr = obs_val.validate(term_ids)

The validator returns back an instance of :class:`hpotk.validate.ValidationResults` with the validation output.
We can check for presence of issues in the input:

.. doctest:: check-consistency

  >>> vr.is_ok()
  False

The input is *not* OK, so we should look at the issues in greater detail:

.. doctest:: check-consistency

  >>> for validation_result in vr.results:
  ...   print(validation_result)
  ValidationResult(level=<ValidationLevel.WARNING: 1>, category='obsolete_term_id_is_used', message='Using the obsolete HP:0001505 instead of HP:0001166 for Arachnodactyly')

We see that the `HP:0001505` is obsolete and `HP:0001166` should be used as the new *Arachnodactyly* identifier.


Phenotypic features should be descendants of *Phenotypic abnormality*
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

HPO hierarchy has several major branches to uniquely represent concepts such as clinical modifiers, modes of inheritance,
and past medical medical history. However, the signs and symptoms should be encoded into descendants
of *Phenotypic abnormality*.

:class:`hpotk.validate.PhenotypicAbnormalityValidator` checks that all identifiers correspond to descendants
of *Phenotypic abnormality*:

Let's test that this is valid for the patient features:

.. doctest:: check-consistency

  >>> from hpotk.validate import PhenotypicAbnormalityValidator
  >>> pa_val = PhenotypicAbnormalityValidator(hpo)

  >>> vr = pa_val.validate(term_ids)
  >>> vr.is_ok()
  True

Yes, the all term ids represent the descendants of *Phenotypic abnormality*.


Phenotypic features should not violate the annotation propagation rule
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Last and most importantly, let's discuss the concept of annotation redundancy.
HPO uses `is_a` to represent the edges of the ontology hierarchy graph. The edges model the "parent-child"
relationships between two ontology concepts (the object subsumes the subject).

When using HPO concepts to encode clinical features of an individual, presence of a concept implies presence
of all ancestral concepts. This is also known as the "True path rule", where the annotation "propagates" across
the concept ancestors.

In general, using the same annotation more than once is considered an error (e.g. annotate the subject with *Focal clonic seizure*
and *Focal clonic seizure*). However, thanks to the True path rule, using a concept and its ancestor is an offender
of a similar kind.

:class:`hpotk.validate.AnnotationPropagationValidator` checks if a set of terms violate the annotation propagation rule
- if a collection of concepts contains a term and its ancestor.

.. doctest:: check-consistency

  >>> from hpotk.validate import AnnotationPropagationValidator
  >>> ap_val = AnnotationPropagationValidator(hpo)

  >>> vr = ap_val.validate(term_ids)
  >>> vr.is_ok()
  False

There seems to an issue. Let's break it down:

.. doctest:: check-consistency

  >>> for validation_result in vr.results:
  ...   print(validation_result.level)
  ...   print(validation_result.category)
  ...   print(validation_result.message)
  ValidationLevel.ERROR
  annotation_propagation
  Terms should not contain both present Focal clonic seizure [HP:0002266] and its present or excluded ancestor Seizure [HP:0001250]

The validator points out that *Seizure* is an ancestor of *Focal clonic seizure* and should, therefore, not be used
as an annotation of the individual.

Validation pipeline
^^^^^^^^^^^^^^^^^^^

For greater convenience, the validators can be integrated and run on the input at the same time:

.. doctest:: check-consistency

  >>> from hpotk.validate import ValidationRunner

  >>> # Create a validation runner
  >>> runner = ValidationRunner(validators=(obs_val, pa_val, ap_val))

  >>> # Validate the input features
  >>> vr = runner.validate_all(term_ids)
  >>> vr.is_ok()
  False

  >>> for validation_result in vr.results:
  ...   print(validation_result)
  ValidationResult(level=<ValidationLevel.WARNING: 1>, category='obsolete_term_id_is_used', message='Using the obsolete HP:0001505 instead of HP:0001166 for Arachnodactyly')
  ValidationResult(level=<ValidationLevel.ERROR: 2>, category='annotation_propagation', message='Terms should not contain both present Focal clonic seizure [HP:0002266] and its present or excluded ancestor Seizure [HP:0001250]')

:class:`hpotk.validate.ValidationRunner` applies several validators and aggregates the issues into
:class:`hpotk.validate.ValidationResults`. We can check if the input passed the validation and if not, we can go through
the issues.
