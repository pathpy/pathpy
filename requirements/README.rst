pathpy requirements
===================

Any application typically has a set of dependencies that are required for that
application to work. The requirements file is a way to specify and install
specific set of package dependencies at once.

Requirements
------------

pathpy.txt
  Default requirements to install the module
test.txt
  Requirements for running test suite
doc.txt
  Requirements for building the documentation (see `../doc/`)

Examples
--------

Installing requirements
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -U -r requirements/pathpy.txt


Running the tests
~~~~~~~~~~~~~~~~~

.. code-block:: bash

   pip install -U -r requirements/pathpy.txt
   pip install -U -r requirements/test.txt


Building the doc
~~~~~~~~~~~~~~~~
.. code-block:: bash

    pip install -U -r requirements/pathpy.txt
    pip install -U -r requirements/doc.txt
