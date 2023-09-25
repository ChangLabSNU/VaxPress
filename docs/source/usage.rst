*****
Usage
*****

There are 2 required arguments to run VaxPress: ``-i``, ``-o``.
``-i`` specifies the input file path, and ``-o`` specifies the
output directory path.

Command-line below is an example of basic VaxPress usage. You might
follow it:
::
    
    # To see a full list of available options, use vaxpress --help 
    vaxpress -h
   
    # Example command to run VaxPress
    # Specify input file, output directory, number of iterations, and number of processes to use 
    vaxpress -i {path_to_input.fa} -o {path_to_output_directory} --iterations {n_iterations} -p {n_processes}

===========
Input Files
===========

VaxPress requires an input file in FASTA format containing the
CDS(CoDing Sequence) sequence to be optimized. Protein sequence
in FASTA format is also available as an input, using ``--protein``
option.

====================
Number of Iterations
====================

By default, the ``--iterations`` option is set to 10. For a
comprehensive optimization, it's suggested to use a minimum of 500
iterations. However, the ideal number of iterations can vary based
on the input's length, composition, and chosen optimization settings.
Note that the optimization process might halt before completing all
specified iterations if no improvement is detected over several
consecutive cycles. Guide to set the appropriate iteration numbers
and other optimization parameters can be found in :ref:`tuning-parameters`
section.

==================
Multi-Core Support
==================

You can use multiple CPU cores for optimization with the ``-p`` or
``--processes`` option. By default, VaxPress uses only one core.
Adding ``--processes N`` option paralellizes the calculation needed
for the scoring functions and secondary structure prediction in
each iteration. Assigning more cores will speed up the optimization
process, as ``N`` specifies the maximum number of cores that the
calculation can be distributed. However, suitable number of cores
depends on the amount of available computational resources.


====================================
Adjusting the Fitness Scoring Scheme
====================================

VaxPress optimizes synonymous codon selections to potentially enhance
the fitness of coding sequences for mRNA vaccines. This fitness
is derived from a cumulative score of various metrics, including
the codon adaptation index, GC ratio, among others. To emphasize
or de-emphasize a specific feature, simply adjust its weight.

To fine-tune the optimization, adjust the weights of individual
scoring functions using the ``--{func}-weight`` option. Setting a
function's weight to ``0`` effectively disables it.

.. code-block:: bash

    # Concentrate on the stable secondary structure (more weight to the MFE)
    vaxpress -i spike.fa -o result-spike --mfe-weights 10

    # Turn off the consideration of repeated sequences
    vaxpress -i spike.fa -o result-spike --repeats-weight 0

VaxPress allows users to add their custom scoring functions. See
:ref:`label-addon` section.

A deeper understanding of the scoring functions' principles is
available on the :doc:`Algorithmic Details </algorithmic_details>`
section.

.. _lineardesign:

==================================================
Using LinearDesign for Optimization Initialization
==================================================

LinearDesign offers ultra-fast optimization, focusing on near-optimal
MFE and CAI values. By using the ``--lineardesign`` option, VaxPress
invokes LinearDesign internally then begins its optimization with
a sequence already refined by LinearDesign. Subsequent VaxPress
optimizations further improves the sequences for features like
secondary structures near the start codon, uridine count, in-cell
stability, tandem repeats, and local GC content. Below is the
command line example for using ``--lineardesign`` option:

.. code-block:: bash

    # Running VaxPress with LinearDesign
    vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 500 --lineardesign 1.0 \
         --lineardesign-dir /path/to/LinearDesign \
         --conservative-start 10 --initial-mutation-rate 0.01

Detailed information including the meaning of each parameter and
its recommended values is available on :ref:`using-lineardesign`
section. To see the list of all options related to LinearDesign,
see :ref:`LinearDesign options <label-linopts>`


============
Output Files
============

Once you've run VaxPress, the specified output directory will contain
the following five files:

- ``report.html``: A summary report detailing the result and
  optimization process. The report contains the following informations:

  1. Basic information on the task including sequence name and command line.

  .. image:: _images/task_information.png
        :width: 500px
        :alt: checkpoints.tsv
        :align: center

  2. Information about the optimized sequence: metric comparison
     between initial & optimized score
  
  .. image:: _images/optimized_sequence.png
        :width: 500px
        :alt: checkpoints.tsv
        :align: center

  3. Interactive plot showing the predicted secondary structure of
     the output sequence
   
  .. image:: _images/predicted_secondary_structure.png
        :width: 500px
        :alt: checkpoints.tsv
        :align: center

  4. Plots showing the changes of each metrics and parameters over
     the iterations.
   
  .. image:: _images/optimization_process.png
        :width: 500px
        :alt: checkpoints.tsv
        :align: center

  5. Parameters used in the corresponding VaxPress run. This
     information is also stored in ``parameters.json``.
   
  .. image:: _images/parameters.png
        :width: 500px
        :alt: checkpoints.tsv
        :align: center

- ``best-sequence.fasta``:  The refined coding sequence.

- ``checkpoints.tsv``: The best sequences and its evaluation results
  at each iteration.
  
  .. image:: _images/checkpoints.tsv_example.png
        :width: 500px
        :alt: checkpoints.tsv
        :align: center

- ``log.txt``: Contains the logs that were displayed in the console.

- ``parameters.json``: Contains the parameters employed for the
  optimization. This file can be feeded to VaxPress with the ``--preset``
  option to duplicate the set-up for other sequence. To check the
  detailed information on how to use ``--preset``, see :ref:`execution
  options`.