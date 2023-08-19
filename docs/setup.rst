.. _setup:

=====
Setup
=====

This document describes how to install stable or the bleeding edge code into your Python environment.

Stable code
^^^^^^^^^^^

Installing HPO toolkit is easy - we publish the releases on `PyPi <https://pypi.org/project/hpo-toolkit>`_.

Therefore, the latest stable release can be installed by running::

  $ python3 -m pip install hpo-toolkit

The bleeding edge code
^^^^^^^^^^^^^^^^^^^^^^

To access the bleeding edge features, the development version can be installed by::

  $ git clone https://github.com/TheJacksonLaboratory/hpo-toolkit.git
  $ cd hpo-toolkit
  $ git checkout development && git pull
  $ python3 -m pip install .

This will clone the Git repository into your machine, switch to the `development` branch, and install HPO toolkit into
the active Python environment, assuming you have privileges to install packages.

That's about it!