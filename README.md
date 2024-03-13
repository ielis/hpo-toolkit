# hpo-toolkit

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hpo-toolkit)
![PyPi downloads](https://img.shields.io/pypi/dm/hpo-toolkit.svg?label=Pypi%20downloads)
![Build status](https://img.shields.io/github/actions/workflow/status/TheJacksonLaboratory/hpo-toolkit/python_ci.yml)
[![GitHub release](https://img.shields.io/github/release/TheJacksonLaboratory/hpo-toolkit.svg)](https://github.com/TheJacksonLaboratory/hpo-toolkit/releases)

A toolkit for working with Human Phenotype Ontology (HPO) and HPO disease annotations in Python.

## Example

Loading HPO is as simple as:

```python
import hpotk

store = hpotk.configure_ontology_store()
hpo = store.load_hpo()
```

Now you have the concepts and the hierarchy of the latest HPO release at your fingertips.

Next, load the HPO disease annotations by running:

```python
from hpotk.annotations.load.hpoa import SimpleHpoaDiseaseLoader

hpoa_path = 'https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2023-10-09/phenotype.hpoa'

loader = SimpleHpoaDiseaseLoader(hpo)
diseases = loader.load(hpoa_path)

assert len(diseases) == 12_468
```

You got yourself phenotype annotations of 12,468 rare diseases.

## Learn more

Find more info in our detailed documentation:

- [Stable documentation](https://thejacksonlaboratory.github.io/hpo-toolkit/stable) (last release on `main` branch)
- [Latest documentation](https://thejacksonlaboratory.github.io/hpo-toolkit/latest) (bleeding edge, latest commit on `development` branch)
