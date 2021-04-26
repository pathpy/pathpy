.. _api_ref:

.. currentmodule:: pathpy

API reference
=============

.. _classes_api:

Base classes
------------

.. autosummary::
    :toctree: generated

     Node
     Edge
     Path
     Network

.. _algorithms_api:


Converting objects
------------------

.. autosummary::
    :toctree:

    converters.networkx
    converters.to_paths

Plotting objects
----------------

.. autosummary::
    :toctree:

    plot

Reading and writing network data
--------------------------------

.. _io_api:

.. autosummary::
    :toctree: generated

    io.konect
    io.graphtool
    io.csv
    io.sql
    io.graphml

Generating graphs
-----------------

.. _generators_api:

.. autosummary::
    :toctree: generated

    generators.lattice
    generators.random_graphs

Statistical analysis
--------------------

.. autosummary::
    :toctree: generated

    statistics.clustering
    statistics.degrees
    statistics.likelihoods
    statistics.modularity
    statistics.subpaths


Graph algorithms
----------------

.. autosummary::
    :toctree: generated

    algorithms.centralities
    algorithms.community_detection
    algorithms.components
    algorithms.shortest_paths
    algorithms.trees
    algorithms.evaluation

.. _algorithms_api:

Simulating dynamical processes
------------------------------

.. _processes_api:

.. autosummary::
    :toctree: generated

    processes.random_walk