.. _setup:

=====
Setup
=====

This document describes how to install the stable version or the bleeding edge code into your Python environment.

Stable code
^^^^^^^^^^^

Installing HPO toolkit is easy - we publish the releases on `PyPi <https://pypi.org/project/hpo-toolkit>`_.

Therefore, the latest stable release can be installed by running::

  python3 -m pip install hpo-toolkit

The bleeding edge code
^^^^^^^^^^^^^^^^^^^^^^

To access the bleeding edge features, the development version can be installed by::

  git clone https://github.com/TheJacksonLaboratory/hpo-toolkit.git
  cd hpo-toolkit
  git checkout development && git pull
  python3 -m pip install .

This will clone the Git repository into your machine, switch to the `development` branch, and install HPO toolkit into
the active Python environment, assuming you have privileges to install packages.

Run tests
^^^^^^^^^

The contributors may want to run the unit tests and the integration tests to ensure all features work as expected.

Before running tests, make sure you install HPO toolkit with `test` dependencies::

  python3 -m pip install .[test]

The unit tests, integration tests, doctests, and the tutorial scripts can the be running by invoking the `pytest` runner::

  pytest

  The library *must* be installed in the environment before running all tests. Otherwise, the test discovery will fail.

Run benches
^^^^^^^^^^^

Bench suites provide an idea about the performance of the library.
Running a bench requires checking out the GitHub repository and installing HPO toolkit with `bench` dependencies::

  git clone https://github.com/TheJacksonLaboratory/hpo-toolkit.git
  cd hpo-toolkit
  python3 -m pip install .[bench]

Then, running a bench suite is as easy as::

  REVISION=$(git rev-parse --short HEAD)
  python3 benches/graph_traversal.py --hpo /path/to/hp.json --revision ${REVISION}

The `graph_traversal` bench suite measures mostly the graph traversal performance.
The suite stores the bench results in a CSV file that is written into the current folder.
The CSV file reports throughput (`ops/s`) of various methods.

.. note::

  The suite is under development and thus subject to change.

That's about it!