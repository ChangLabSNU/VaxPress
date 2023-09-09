Welcome to VaxPress's documentation!
************************************

VaxPress is a codon optimizer platform tailored for mRNA vaccine development.
It refines coding sequences starting from protein or RNA sequences to boost both storage stability and in vivo protein expression.
Plus, additional properties can be easily programmed into the optimization process with just a few lines of code via a pluggable interface.
Due to its versatile nature, VaxPress can be used not only for mRNA vaccine development, but also for mRNA-based therapeutics and the other codon optimizations for various purposes.

.. _prerequisites:
-------------
Prerequisites
-------------

VaxPress is a python-based tool.
To install VaxPress via ``pip`` or ``conda``, you will need a python installation (version >= ??).

.. note::
    If you install VaxPress via pip, ``R``, ``rpy2`` (version >= 3.0) and ``iCodon`` aren't included as dependencies.
    If you want to utilize iCodon's predicted stability in the fitness function, you'll need to install these separately.
    For iCodon installation, see `iCodon's GitHub page <https://github.com/santiago1234/iCodon/>`_.

To install via ``singularity``, you will need to install `Singularity CE <https://sylabs.io/singularity/>`_ first.

To use ``--lineardesign`` options, `LinearDesign <https://github.com/LinearDesignSoftware/LinearDesign>`_ installation is required apart from VaxPress installation.


------------
Installation
------------

You can install VaxPress via ``pip``:
::
    # To install using pip
    pip install vaxpress

    # To install using pip with LinearFold (only for non-commercial uses)
    pip install 'vaxpress[nonfree]'

    # To install from the Github
    git clone https://github.com/ChangLabSNU/VaxPress.git
    cd VaxPress
    pip install .

VaxPress ``conda`` package is also available:
::
    conda install -c changlabsnu -c bioconda -c conda-forge vaxpress

To install using Singularity, you will first need to install `Singularity CE <https://sylabs.io/singularity/>`_.
Once Singularity is installed, you can download the VaxPress image from this GitHub repository and run using the following command:
::
    singularity vaxpress.sif ...

It is recommended that VaxPress be installed in a control compute environment.
See `the python documentation for preparing virtual environments <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`_

-----------
Quick Start
-----------

There are 2 required arguments to run VaxPress: ``-i``, ``-o``.
``-i`` specifies the input file path, and ``-o`` specifies the output directory path.
Basic command-line usage of vaxpress looks like below:
::
    # To see a full list of available options, use vaxpress --help 
    vaxpress -h
   
    # Example command to run VaxPress
    # Specify input file, output directory, number of iterations, and number of processes to use 
    vaxpress -i {path_to_input.fa} -o {path_to_output_directory} --iterations {n_iterations} -p {n_processes}

============
Input Files
============
VaxPress requires an input file in FASTA format containing the CDS sequence to be optimized.
Protein sequence in FASTA format is also available as an input, using ``--protein`` option.


=================
Number of Iterations
=================
By default, the ``--iterations`` option is set to 10.
For a comprehensive optimization, it's suggested to use a minimum of 500 iterations.
However, the ideal number of iterations can vary based on the input's length, composition, and chosen optimization settings.
Note that the optimization process might halt before completing all specified iterations if no improvement is detected over several consecutive cycles.
Guide to set the appropriate iteration numbers and other optimization parameters can be found in :doc:`guide to set parameters </guide_to_set_parameters>` section.

==================
Multi-Core Support
==================
You can use multiple CPU cores for optimization with the ``-p`` or ``--processes`` option.


===================================
Adjusting the Fitness Scoring Scheme
===================================
VaxPress optimizes synonymous codon selections to potentially enhance the fitness of coding sequences for mRNA vaccines.
This fitness is derived from a cumulative score of various metrics, including the codon adaptation index, GC ratio, among others.
To emphasize or de-emphasize a specific feature, simply adjust its weight.

- To fine-tune the optimization, adjust the weights of individual scoring functions using the ``--{func}-weight`` option. Setting a function's weight to ``0`` effectively disables it.

.. code-block:: bash

    # Concentrate on the stable secondary structure (more weight to the MFE)
    vaxpress -i spike.fa -o result-spike --mfe-weights 10

    # Turn off the consideration of repeated sequences
    vaxpress -i spike.fa -o result-spike --repeats-weight 0

- VaxPress allows users to add their custom scoring functions. See :doc:`adding custom scoring functions </adding_scorefunc>` section.

A deeper understanding of the scoring functions' principles is available on the :doc:`Algorithmic Details </algorithmic_details>` section.


====================================================
Using LinearDesign for Optimization Initialization
====================================================
See :doc:`Using LinearDesign for Optimization Initialization </running_with_lineardesign>` section.

=============
Output Files
=============
Once you've run VaxPress, the specified output directory will contain the following five files:

- ``report.html``: A summary report detailing the result and optimization process.

- ``best-sequence.fasta``:  The refined coding sequence.

- ``checkpoints.tsv``: The best sequences and its evaluation results at each iteration.

- ``log.txt``: Contains the logs that were displayed in the console.

- ``parameters.json``: Contains the parameters employed for the optimization. This file can be feeded to VaxPress with the ``--preset`` option to duplicate the set-up for other sequence.




--------
Contents
--------
.. toctree::
   :maxdepth: 2

   tutorial
   algorithmic_details
   adding_scorefunc
   running_with_lineardesign
   execution_input_output_options
   optimization_parameters
   fitness_function_parameters
   guide_to_set_parameters
   usage
   troubleshooting

------------------
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`