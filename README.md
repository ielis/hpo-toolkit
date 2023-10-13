# hpo-toolkit

![Build status](https://img.shields.io/github/actions/workflow/status/TheJacksonLaboratory/hpo-toolkit/python_ci.yml)
![PyPi downloads](https://img.shields.io/pypi/dm/hpo-toolkit.svg?label=Pypi%20downloads)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hpo-toolkit)

A toolkit for working with Human Phenotype Ontology in Python.

Loading HPO is as simple as:

```python
import hpotk

hpo = hpotk.load_ontology('http://purl.obolibrary.org/obo/hp.json')
```

Loading HPO annotations is accomplished by running:

```python
from hpotk.annotations.load.hpoa import SimpleHpoaDiseaseLoader

hpoa_path = 'https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2023-10-09/phenotype.hpoa'

loader = SimpleHpoaDiseaseLoader(hpo)
diseases = loader.load(hpoa_path)

# Phenotype annotations for 12,468 rare diseases is at your fingertips.
assert len(diseases) == 12_468
```

Check out the User guide and the API reference for more info:

- [Stable documentation](https://thejacksonlaboratory.github.io/hpo-toolkit/stable) (last release on `main` branch)
- [Latest documentation](https://thejacksonlaboratory.github.io/hpo-toolkit/latest) (bleeding edge, latest commit on `development` branch)
