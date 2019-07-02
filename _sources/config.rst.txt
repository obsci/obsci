Config
======

obsci needs to know which tests should be executed.

_obsci from a OBS package
-------------------------

:term:`_obsci` is a configuration file (in YAML format ) that can be stored
in :term:`OBS` packages next to the other package files (like tarballs,
RPM spec files, ...).

.. code-block:: yaml

  ---
  tests:
    - name: first-test

The test name (in this example, *first-test*) needs to be a file (eg. a shell
script) that is in the same package. This script will be executed as a
test.

_obsci from a OBS project
-------------------------
To be able to define tests for a whole project, the OBS project config can
be adjusted (via valid JSON) to add tests from other packages.

.. code-block::

   _obsci: '{"test_packages": [{"project": "home:tbechtold:branches:devel:languages:python", "package": "python-Jinja2"}]}'

This project config would add all tests that are found in the package *python-Jinaj2*
from the project *home:tbechtold:branches:devel:languages:python*.
With that, it is possible to define packages that contain tests and reference
theses packages via the project config.

_obsci package schema validation
--------------------------------
The jsonschema that is used to validate the `_obsci` file from a package is:

.. literalinclude:: ../../obsci/worker/config_package_schema.json

_obsci_packages project config schema validation
------------------------------------------------
The jsonschema that is used to validate the `_obsci` key/value pair from
the OBS project configs is:

.. literalinclude:: ../../obsci/worker/config_project_schema.json
