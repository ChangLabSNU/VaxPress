*****
Usage
*****

There are two arguments that are required in order to run VaxPress:
``-i`` and ``-o``, for the paths to the input file and the output
directory, respectively.

::
    
    # To see a full list of available options, use vaxpress --help 
    vaxpress -h
   
    # Example command to run VaxPress
    # Specify input file, output directory, number of iterations, and number of processes to use 
    vaxpress -i {path_to_input.fa} -o {path_to_output_directory} --iterations {n_iterations} -p {n_processes}

===================
Input File (``-i``)
===================

VaxPress requires a FASTA format input file that contains the CDS
(CoDing Sequence) to be optimized. In case the FASTA file holds a
protein sequence, the additional ``--protein`` switch is required.

=======================================
Number of Iterations (``--iterations``)
=======================================

The ``--iterations`` option is set to ``10`` by default. However,
for thorough optimization, it's recommended to use at least ``500``
iterations. The optimal number of iterations may differ depending
on the length, composition of the input, and the selected optimization
settings. It's important to note that the optimization process may
stop before completing all the specified iterations if no progress
is observed over several consecutive cycles. Guidelines for setting
the appropriate number of iterations and other optimization parameters
can be found in the :ref:`tuning-parameters` section.

===========================
Multi-Core Support (``-p``)
===========================

You can use multiple CPU cores for optimization with the ``-p`` or
``--processes`` option. The ``--processes N`` option allows the
parallelization of calculations required for scoring functions and
secondary structure prediction in each iteration. The ``N`` denotes
the maximum number of cores that the computation can be distributed
across, thus enhancing the speed of the optimization process.

====================================
Adjusting the Fitness Scoring Scheme
====================================

VaxPress is designed to optimize synonymous codon selections,
potentially improving the fitness of coding sequences for mRNA
vaccines. This fitness is determined by a cumulative score of various
metrics, such as the codon adaptation index and GC content. You can
adjust the weight of a specific feature to emphasize or de-emphasize
it.

To fine-tune the optimization process, use the ``--{func}-weight``
option to adjust the weights of individual scoring functions. Setting
a function's weight to ``0`` effectively disables it.

.. code-block:: bash

    # Concentrate on the stable secondary structure (more weight to the MFE)
    vaxpress -i spike.fa -o result-spike --mfe-weights 10

    # Turn off the consideration of repeated sequences
    vaxpress -i spike.fa -o result-spike --repeats-weight 0

VaxPress also allows the addition of custom scoring functions. More
information on this can be found in the :ref:`label-addon` section.

For a comprehensive understanding of how VaxPress determines sequence
optimality, refer to the :doc:`algorithmic_details` section.

.. _lineardesign-simple:

==================================================
Using LinearDesign for Optimization Initialization
==================================================

VaxPress also provides the ``--lineardesign`` option. This initiates
optimization using a sequence pre-refined by *LinearDesign.* It
allows VaxPress to start its optimization process with a sequence
that already possesses a near-optimal MFE and CAI. Further optimizations
then improve the sequences for features such as secondary structures
near the start codon, uridine count, in-cell stability, in-solution
stability, tandem repeats, and local GC content.

.. code-block:: bash

    # Running VaxPress with LinearDesign
    vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 500 --lineardesign 1.0 \
         --lineardesign-dir /path/to/LinearDesign \
         --conservative-start 10 --initial-mutation-rate 0.01

For a detailed information, refer to the :ref:`using-lineardesign`
section. The :ref:`LinearDesign options <label-linopts>` section
provides a comprehensive list of all options related to *LinearDesign.*

===============
Output (``-o``)
===============

Once you've run VaxPress, the specified output directory will contain
the following five files:

- ``report.html``: The report provides a detailed summary of the
  results and the optimization process. It includes the following
  information:

  #. Basic sequence information on the task including the sequence name
     and command line.

     .. image:: _images/task_information.png
        :width: 500px
        :alt: Task information in the report
        :align: center

  #. The optimized sequence information includes a comparison of
     the initial and optimized scores.
  
     .. image:: _images/optimized_sequence.png
        :width: 500px
        :alt: Optimized sequence information in the report
        :align: center

  #. An interactive view that displays the predicted secondary structure
     of the output sequence.
   
     .. image:: _images/predicted_secondary_structure.png
        :width: 500px
        :alt: Interactive structure view in the report
        :align: center

  #. Plots illustrate the changes in metrics and parameters over
     the iterations.
   
     .. image:: _images/optimization_process.png
        :width: 500px
        :alt: Plots for metric changes over iterations in the report
        :align: center

  #. Parameters used in the corresponding VaxPress run. This
     information is also stored in ``parameters.json``.
   
     .. image:: _images/parameters.png
        :width: 500px
        :alt: Parameters for the optimization in the report
        :align: center

- ``best-sequence.fasta``: The refined coding sequence.

- ``checkpoints.tsv``: The best sequences and its evaluation results
  at each iteration.
  
  .. image:: _images/checkpoints.tsv_example.png
        :width: 500px
        :alt: Sequence checkpoints
        :align: center

- ``log.txt``: Contains the logs that were displayed in the console.

- ``parameters.json``: Holds the optimization parameters along with
  the other command line options. This file can be used with the
  ``--preset`` option in VaxPress to replicate the optimization
  setup for other sequences. For detailed information on using
  ``--preset``, refer to :ref:`execution options`.