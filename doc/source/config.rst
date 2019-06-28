Config
======

obsci needs to know which tests should be executed.

_obsci
------

:term:`_obsci` is a configuration file (in YAML format ) that can be stored
in :term:`OBS` packages next to the other package files (like tarballs,
RPM spec files, ...).

.. code-block:: yaml

  ---
  tests:
    - name: first-test

_obsci schema validation
------------------------
The jsonschema that is used to validate the `_obsci` file is:

.. literalinclude:: ../../obsci/worker/config_package_schema.json
