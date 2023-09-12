Usage
*********

This page demonstrates some additional ways of how VaxPress can be used.
Basic usage of VaxPress is described in :doc:`Quick Start </index>` section.


==================================================
Removing tandem repeats from LindearDesign output
==================================================
Overall, VaxPress can consist a workflow starting from LinearDesign.
(See :doc:`Using LinearDesign for Optimization Initialization </running_with_lineardesign>` section for detailed information about the related options and parameters.)
In this usage, VaxPress refines the MFE- or CAI-optimized sequence from LinearDesign on the other factors not considered in LinearDesign.

For example, VaxPress can remove tandem repeats from the LinearDesign output.

mRNA manufacturing is a significant process of mRNA vaccine development.
However, the presence of repeated sequences cause severe difficulties in the manufacturing process.
As LinearDesign algorithm doesn't consider repeats, the output sequence from LinearDesign may contain repeated sequences.
Especially, when the ``lambda`` parameter is set high(which means high weight on CAI), the occurence of tandem repeat is highly probable since the codon with high CAI score is always favored.
::
    # Example command to get LinearDesign-VaxPress optimized sequence with tandem repeats removed
    # MFE weight is set high to preserve the LinearDesign-optimized secondary structure
    # High weight set on Tandem Repeats, while CAI weight is set minimal.
    vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 500 --lineardesign 1.0 \
         --lineardesign-dir /path/to/LinearDesign \
         --conservative-start 10 --initial-mutation-rate 0.01 \
         --default-off \
         --mfe-weight 10 --repeats-weight 10 --cai-weight 1 --gc-weight 3 --start-str-weight 1


=============================================================
Using VaxPress as a User-friendly Interface to LinearDesign
=============================================================
Using ``--conservative-start N`` option only generates mutations in the start codon region during the initial N number of iterations,
leaving the rest of the sequence as it is.
Therefore, by assigning the same parameter for ``--conservative-start`` and ``--iterations`` options,
VaxPress can be used as a convenient front-end interface for LinearDesign optimization.

Using LinearDesign through VaxPress interface offers several advantages:

- LinearDesign can be run without python2 dependency in VaxPress.
- In addition to the optimized sequence output by LinearDesign, VaxPress produces output report that contains detailed information about the sequence including the visualization of secondary structure and evaluation results of various metrics.
- When using LinearDesign alone, several N-terminal amino acids should be manually removed before running the optimization to prevent folded structures in the start codon region. This process is run automatically in VaxPress with `--lineardesign-omit-start`(default = 5) option.
- While LinearDesign only accepts protein sequence, mRNA sequence can be directly used as an input in VaxPress.

.. code-block:: bash

    # Example usage of VaxPress as an interface to LinearDesign
    vaxpress -i spike.fa -o results-spike --processes 36 \
            --iterations 10 --lineardesign 1.0 \
            --conservative-start 10 --initial-mutation-rate 0.01 \
            --lineardesign-dir /path/to/LinearDesign \

=============================
Evaluating the given sequence
=============================

By setting ``--iterations`` to ``0``, VaxPress provides a convenient method to just evaluate a given sequence with no further optimization.
Output report will be generated containing all the results from VaxPress's scoring functions, including the visualization of secondary structure.