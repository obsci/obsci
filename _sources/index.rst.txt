Welcome to OBSCI - a CI system for the Open Build Service
=========================================================

:term:`OBSCI` is a CI system for testing :term:`OBS` packages. `OBSCI`
is pretty new and there are plenty of things to do. Currently the
following workflow is supported:

* Use docker containers as :term:`Test environment`
* Defining tests in a OBS package via a :term:`_obsci` config file
* Installing RPM :term:`Test Subject` in the container

Quickstart
----------
#. :term:`OBSCI` can be directly installed from git into a virtual environment:

.. code-block:: console

   virtualenv obsci-venv
   source obsci-venv/bin/activate
   pip install git+https://github.com/obsci/obsci.git -e .[worker]

#. Add a `_obsci` file which defines tests to your package. The file should look
   like::

.. code-block:: yaml

   ---
   tests:
     - name: first_test.sh

#. Add a `first_test.sh` file to your package. This file is the actual test.
   If the exit code is 0, the test succeeded, otherwise it failed.
   `first_test.sh` could be written in any language. The only thing that
   matters is the exit code.

.. code-block:: sh

   #!/bin/bash
   echo "This is my testscript"
   exit 0

#. How the tests can be executed with the obsci-worker:

.. code-block:: console

   obsci-worker --obs-username tbechtold --obs-password mypassword \
       home:tbechtold openSUSE_Leap_15.1 x86_64 python-Jinja2

Here, `obs-username` and `obs-password` are needed to be able to talk
to the :term:`OBS Api`.
`home:tbechtold` is the OBS project and `python-Jinja2` the OBS package.
This package must contain the `first_test.sh` and `_obsci` file.


.. toctree::
   :hidden:

   config.rst
   glossary.rst
