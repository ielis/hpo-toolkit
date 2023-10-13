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

The contributors may want to run the unit tests and the integration tests to ensure the features work as expected.
Hpo-toolkit's tests use a combination of `unittest` and `ddt`. The tests are run as::

  python3 -m unittest discover -s src -p _test*.py
  python3 -m unittest discover -s tests

.. note::

  The library *must* be installed in the environment before running the tests. Otherwise, the test discovery will fail.

That's about it!