*************
Options
*************



Input/Output and Execution Options
*************************************

List of all arguments related to input/output and general execution of the program.


- ``-h``, ``--help``

  Show help messages for Vaxpress and exit.

---------------------
Input/Output Options
---------------------

====================
Required Arguments
====================
- ``-i``, ``--input`` FILE

  Path to the input fasta file containing the CDS sequence.
- ``-o``, ``--output`` DIR

  Path to the output directory.

===================
Optional Arguments
===================
- ``--protein``

  Input is a protein sequence.
- ``--overwrite``
  
  Overwrite output directory if it already exists.
- ``-q``, ``--quiet``
  
  Do not print progress messages to stdout.
- ``--print-top`` N
  
  Print top and bottom N sequences. (default: 10)
- ``--report-interval`` MIN
  
  Report interval in minutes. In other words, report.html will be updated by this time interval. (default: 5)
- ``--version``

  show program's version number and exit.

.. _execution options:

---------------------
Execution Options
---------------------
- ``--preset`` FILE
  
  Use preset values in ``parameters.json``, which is one of the output files from the VaxPress run. 
  If some of the options are specified along with ``--preset``, the specified arguments including addons will override the preset values.

  Example command to use preset values::

    vaxpress -i {path_to_input.fa} \
             -o {path_to_output_directory} \
             --preset {path_to_parameters.json}

- ``--addon`` FILE

  Load a third-party fitness function.

  Example command to use a third-party fitness function::

    vaxpress -i {path_to_input.fa} \
             -o {path_to_output_directory} \
             --iterations {n_iterations} \
             -p {n_processes} \
             --addon {path_to_addon.py}

For detailed information on how to use a third-party fitness function, please refer to the :doc:`addon section </adding_scorefunc>` of this documentation.

- ``p``, ``--processes`` N

  Number of processes to use (default: 4)


- ``seed`` NUMBER

  Random seed (default: 922)

- ``--codon-table`` NAME

  Codon table that VaxPress refers to. (default: standard)
  Codon tables are imported from `Bio.Data.CodonTable module <https://biopython.org/docs/1.75/api/Bio.Data.CodonTable.html>`_. To check for the full list of supported codon tables, please refer to `NCBI <ftp://ftp.ncbi.nih.gov/entrez/misc/data/gc.prt >`_. (*link is not valid)
  
- ``--random-initialization``

  Randomize all codons at the beginning (default: False)

.. _label-constart:

- ``--conservative-start`` ITER[:WIDTH]
  
  Conserve sequence for the first ITER iterations, except the first WIDTH amino acids. (default WIDTH: 7)
  It's a recommended option to use when running VaxPress with LinearDesign initialization. See :doc:`Running VaxPress with Lineardesign </running_with_lineardesign>` for more information.

- ``--folding-engine`` NAME

  RNA folding engine: vienna or linearfold (default: vienna)

- ``--species`` NAME

  target species (default: human)
  

Optimization Options
*************************************

Below is the list of all arguments related to optimization parameters of the program.
Examples showing the effect of each parameters on the optimization process can be found in the :doc:`Guide to set parameters </guide_to_set_parameters>` section.

- ``--iterations`` N

  Number of iterations (default: 10)
- ``--offsprings`` N

  Number of offsprings per iteration (default: 20)
- ``--survivors`` N

  Number of survivors per iteration (default: 2)
- ``--initial-mutation-rate`` RATE

  Initial mutation rate (default: 0.1)
- ``--winddown-trigger`` N

  Number of iterations with the same best score to trigger mutation stabilization (default: 15) 
  Please refer to :ref:`algorithmic_details <label_WinddownTR>` for detailed explanation.
- ``--winddown-rate`` RATE

  Mutation rate multiplier when mutation stabilization is triggered (default: 0.9)
  Please refer to :ref:`algorithmic_details <label_WinddownTR>` for detailed explanation.
- ``--boost-loop-mutations`` WEIGHT[:START]

 boost mutations in loops after position START by WEIGHT (default: 3:15)



LinearDesign Options 
****************************

- ``--lineardesign`` LAMBDA

  Call LinearDesign to initialize the optimization. 
  ``LAMBDA`` (λ) is a parameter specifying the ratio that MFE and CAI are reflected in the optimization. 
  λ is in (–∞, 0] while λ = 0 means only MFE is considered, and the weight on CAI increases as λ increases. 

- ``--lineardesign-dir`` DIR

  Path to the top directory containing LinearDesign.

- ``--lineardesign-omit-start`` AA

  The number of amino acids to omit from the N-terminus when calling LinearDesign (default: 5). 
  By using this option, generation of folded structures in start codon region while optimizing MFE by LinearDesign can be avioded.




Options related to Fitness Functions
***************************************

List of all arguments related to fitness functions inside VaxPress.

--------
iCodon
--------

- ``--iCodon-weight WEIGHT``
  Scoring weight for iCodon predicted stability (default: 1.0).

------------------------
Codon Adaptation Index
------------------------

- ``--cai-weight WEIGHT``
  Scoring weight for codon adaptation index (default: 3.0).

----------------------------------------
Codon Adaptation Index of Codon-Pairs
----------------------------------------

- ``--bicodon-weight WEIGHT``
  Scoring weight for codon adaptation index of codon-pairs (default: 1.0).

----------
Uridines
----------

- ``--ucount-weight WEIGHT``
  Scoring weight for U count minimizer (default: 3.0).

-----------------
RNA Folding
-----------------

============
MFE
============

- ``--mfe-weight WEIGHT``
  Scoring weight for Minimum Free Energy (MFE) (default: 3.0).


============
Loops
============

- ``--loop-weight WEIGHT``
  Scoring weight for loops (default: 1.5).

- ``--loop-threshold N``
  Minimum count of unfolded bases to be considered as a loop (default: 2).

==========================
Structure near Start Codon
==========================

- ``--start-str-weight WEIGHT``
  Penalty weight for folded start codon region (default: 1).

- ``--start-str-width WIDTH``
  Width in nt of unfolded region near the start codon (default: 15).

==========================
Long Stems
==========================

- ``--longstem-weight WEIGHT``
  Penalty score for long stems (default: 100.0).

- ``--longstem-threshold N``
  Minimum length of stems to avoid (default: 27).

-----------------
Local GC Ratio
-----------------

- ``--gc-weight WEIGHT``
  Scoring weight for GC ratio (default: 3.0).

- ``--gc-window-size SIZE``
  Size of window for GC content calculation (default: 50).

- ``--gc-stride STRIDE``
  Size of stride for GC content calculation (default: 5).

-----------------
Tandem Repeats
-----------------

- ``--repeats-weight WEIGHT``
  Scoring weight for tandem repeats (default: 1.0).

- ``--repeats-min-repeats N``
  Minimum number of repeats to be considered as a tandem repeat (default: 2).

- ``--repeats-min-length LENGTH``
  Minimum length of repeats to be considered as a tandem repeat (default: 10).