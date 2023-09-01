Options related to Fitness Functions
*************************************

List of all arguments related to fitness functions inside VaxPress.

------
iCodon
------

- ``--iCodon-weight WEIGHT``
  Scoring weight for iCodon predicted stability (default: 1.0).

----------------------
Codon Adaptation Index
----------------------

- ``--cai-weight WEIGHT``
  Scoring weight for codon adaptation index (default: 3.0).

--------------------------------------
Codon Adaptation Index of Codon-Pairs
--------------------------------------

- ``--bicodon-weight WEIGHT``
  Scoring weight for codon adaptation index of codon-pairs (default: 1.0).

--------
Uridines
--------

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