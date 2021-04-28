.. _api_ref:

.. currentmodule:: pathpy

API reference
=============

.. _classes_api:

Base classes
------------

.. autosummary::
    :toctree: generated
    :nosignatures:

     Node
     Edge
     Path
     Network

.. _converters_api:

Object-based interoperability
-----------------------------

.. autosummary::
    :toctree: generated
    :nosignatures:
    :recursive:

    converters.to_networkx
    converters.from_networkx

.. _plotting_api:

Visualisations
--------------
..
    see fix for missing links in recursion at https://stackoverflow.com/questions/2701998/sphinx-autodoc-is-not-automatic-enough

.. autosummary::
    :toctree: generated
    :nosignatures:
    :recursive:

    visualisations.plot
    visualisations.layout.layout
    visualisations.layout.Layout


.. _io_api:

Reading and writing network data
--------------------------------

.. autosummary::
    :toctree: generated
    :template: custom-module-template.rst
    :nosignatures:
    :recursive:

    io.pandas
    io.csv
    io.sql
    io.graphtool
    io.graphml
    io.konect
    

.. _generators_api:

Generating graphs
-----------------

.. autosummary::
    :toctree: generated
    :template: custom-module-template.rst
    :nosignatures:
    :recursive:

    generators.lattice
    generators.random_graphs

.. _statistics_api:

Statistical analysis
--------------------

.. autosummary::
    :toctree: generated
    :template: custom-module-template.rst
    :nosignatures:
    :recursive:

    statistics.clustering
    statistics.degrees
    statistics.likelihoods
    statistics.modularity
    statistics.subpaths

.. _algorithms_api:

Algorithms for networks and paths
---------------------------------

.. autosummary::
    :toctree: generated
    :template: custom-module-template.rst
    :nosignatures:
    :recursive:

    algorithms.centralities
    algorithms.community_detection
    algorithms.components
    algorithms.shortest_paths
    algorithms.path_extraction
    algorithms.trees
    algorithms.evaluation

.. _processes_api:

Simulating dynamical processes
------------------------------

.. autosummary::
    :toctree: generated
    :template: custom-module-template.rst
    :nosignatures:
    :recursive:

    processes.random_walk