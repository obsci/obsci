Glossary
========

.. glossary::

   OBSCI
     Open Build Service CI system

   Test Subject
    The items that are to be tested. Examples: RPMs, OCI image, qcow2.
    Currently only RPM packages are supported

   Test
    A callable/runnable piece of code and corresponding test data and mocks
    which exercises and evaluates a test subject.

   Test environment
    Environment where actual test run takes place. Test has direct impact on
    test environment.
    Currently only openSUSE systems with `zypper` as package manager are
    supported.

   Test environment type
     The type of the test environment. Can be something like a container or
     a virtual machine
     Currently only container are supported

   _obsci
     A configuration file in the YAML format to define tests

   OBS
     The Open Build Service project

   OBS Api
     The Open Build Service API. See https://build.opensuse.org/apidocs/index
