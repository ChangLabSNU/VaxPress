Welcome to VaxPress's documentation!
====================================

VaxPress is a codon optimizer specialized for mRNA vaccine design. It pulls
data from the `Open Food Facts database <https://world.openfoodfacts.org/>`_
and offers a *simple* and *intuitive* API.

Check out the :doc:`usage` section for further information, including how to
:ref:`install <installation>` the project.

.. note::
   This project is under active development.

-------------
Prerequisites
-------------

The primary VaxPress run mode requires the Guppy basecaller (version >= 4.0).
See the `community page for download/installation instructions [login required] <https://community.nanoporetech.com/downloads>`_.

VaxPress is a python-based command line software package.
Given a python (version >= 3.5) installation, all other requirements are handled by ``pip`` or ``conda``.

..

   `LinearDesign <https://github.com/nanoporetech/taiyaki>`_ is no longer required to run VaxPress, but installation is required for two specific run modes:

   1) output mapped signal files (for basecall model training)

   2) running the LinearDesign basecalling backend (for neural network designs including experimental layers)

------------
Installation
------------

``pip`` is recommended for VaxPress installation.

::

   pip install vaxpress

``conda`` installation is available, but not fully supported.
``ont_pyguppy_client_lib`` is not available on conda and thus must be installed with ``pip``.

::

   conda install vaxpress
   pip install ont_pyguppy_client_lib

To install from github source for development, the following commands can be run.

::

   git clone https://github.com/nanoporetech/vaxpress
   pip install -e vaxpress/

It is recommended that VaxPress be installed in a control compute environment.
See `the python documentation for preparing virtual environments <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`_

===========
Quick Start
===========

VaxPress must obtain the intermediate output from the basecall neural network.
Guppy (production nanopore basecalling software) is the recommended backend to obtain this output from raw nanopore signal (from FAST5 files).
Nanopore basecalling is compute intensive and thus it is highly recommended that GPU resources are specified (``--devices``) for optimal VaxPress performance.

VaxPress is accessed via the command line interface ``vaxpress`` command.

::

    # vaxpress help (common args)
    vaxpress -h
    # vaxpress help (advanced args)
    vaxpress --help-long

    # Example command to output basecalls, mappings, and 5mC CpG methylation in both per-read (``mod_mappings``) and aggregated (``mods``) formats
    #   Compute settings: GPU devices 0 and 1 with 40 CPU cores
    vaxpress \
        raw_fast5s/ \
        --outputs basecalls mappings mod_mappings mods \
        --reference reference.fa --mod-motif m CG 0 \
        --devices 0 1 --processes 40

This command produces the ``vaxpress_results`` output directory containing all requested output files and logs.
The format for common outputs is described briefly below and in more detail in the `full documentation <https://nanoporetech.github.io/vaxpress/>`_

The above command uses the modified base model included in Guppy.
As of the ``2.3.0`` vaxpress release (March 2021) the models included with Guppy (``4.5.2``) provide the most accurate modified basecalling models.
As more accurate basecalling models are trained, they are first released into the `Rerio repository for research models <https://github.com/nanoporetech/rerio>`_.
Once training pipelines are more thoroughly standardized and tested models will be transferred into Guppy.
The code below shows how to obtain and run the R9.4.1, MinION/GridION, 5mC CpG model from Rerio.
Note that this is the same model now included in Guppy ``4.5.2``.

::

    # Obtain and run R9.4.1, MinION, 5mC CpG model from Rerio
    git clone https://github.com/nanoporetech/rerio
    rerio/download_model.py rerio/basecall_models/res_dna_r941_min_modbases_5mC_CpG_v001
    vaxpress \
        raw_fast5s/ \
        --guppy-params "-d ./rerio/basecall_models/" \
        --guppy-config res_dna_r941_min_modbases_5mC_CpG_v001.cfg \
        --outputs basecalls mappings mod_mappings mods \
        --reference reference.fa --mod-motif m CG 0 \
        --devices 0 1 --processes 40

..

    The path to the ``guppy_basecall_server`` executable is required to run VaxPress.
    By default, VaxPress assumes Guppy (Linux GPU) is installed in the current working directory (i.e. ``./ont-guppy/bin/guppy_basecall_server``).
    Use the ``--guppy-server-path`` argument to specify a different path.

Contents
--------

.. toctree::

   usage


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
