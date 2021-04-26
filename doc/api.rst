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

.. automodule:: io.konect
    members

.. automodule:: io.sql
    members

.. automodule:: io.graphtool
    members

.. automodule:: io.netzschleuder
    members

.. automodule:: io.csv.csv
    members

.. autosummary::
    :toctree: generated

    io.konect.konect
    io.graphtool.graphtool
    io.graphtool.netzschleuder
    io.graphml.graphml
    io.sql.sql
    io.csv.csv.py

Generating graphs
-----------------

.. _processes_api:

.. automodule:: generators.lattice
    members

.. automodule:: generators.random_graphs
    members

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

.. automodule:: processes.random_walk
    members

.. autosummary::
    :toctree: generated

    processes.random_walk.BaseWalk
    processes.random_walk.RandomWalk
    processes.random_walk.VoseAliasSampling