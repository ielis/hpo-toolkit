# hpo-toolkit

![Build status](https://img.shields.io/github/actions/workflow/status/TheJacksonLaboratory/hpo-toolkit/python_ci.yml)
![PyPi downloads](https://img.shields.io/pypi/dm/hpo-toolkit.svg?label=Pypi%20downloads)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hpo-toolkit)

A toolkit for working with Human Phenotype Ontology (HPO) and HPO disease annotations in Python.

## Example

Loading HPO is as simple as:

```python
import hpotk

hpo = hpotk.load_ontology('http://purl.obolibrary.org/obo/hp.json')
```

Now you have HPO concepts and the ontology hierarchy at your fingertips.

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
