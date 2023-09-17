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

==========
Optional Arguments
==========
- ``--protein``

  Input is a protein sequence.
- ``--overwrite``
  
  ==Overwrite output directory if it already exists.
- ``-q``, ``--quiet``
  
  Do not print progress messages to stdout.
- ``--print-top`` N
  
  Print top and bottom N sequences. (default: 10)
- ``--report-interval`` MIN
  
  Report interval in minutes. In other words, report.html will be updated by this time interval. (default: 5)
- ``--version``

  show program's version number and exit.

---------------------
Execution Options
---------------------
- ``--preset`` FILE
  
  In VaxPress, the configuration of the current run including all the parameters is stored in ``parameters.json`` output file.
  This configuration file then can be feeded to VaxPress with the ``--preset`` option to duplicate the set-up for other sequence.
  If some of the options are specified along with ``--preset``, the specified arguments including *addons* will override the preset values.

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

.. _label_constart:
- ``--conservative-start`` ITER[:WIDTH]
  
  Conserve sequence for the first ITER iterations, except the first WIDTH amino acids. (default WIDTH: 7)
  It's a recommended option to use when running VaxPress with LinearDesign initialization. See :doc:`Running VaxPress with Lineardesign </running_with_lineardesign>` for more information.
  ::
    # Example command to conserve sequence for the first 10 iterations except the first 5 amino acids

    vaxpress -i ./testseq/vegfa.fa\
             -o ../test_run\
             --iterations 500\
             --lineardesign 1\
             --lineardesign-dir ../LinearDesign\
             --conservative-start 10:5\

- ``--folding-engine`` NAME

  RNA folding engine: vienna or linearfold (default: vienna)

- ``--species`` NAME

  target species (default: human)
  