***********************
A Tour Through VaxPress
***********************

This guide will show you how to optimize a wild-type mRNA sequence
using VaxPress. As an example, we'll focus on the Hemagglutinin
(HA) protein from the Influenza A virus.

------------------------------
Step 1. Downloading a Sequence
------------------------------

To begin, use the following command to download the complete CDS
sequence of the Influenza A virus's HA protein from a
`GenBank page <https://www.ncbi.nlm.nih.gov/nuccore/FJ981613.1>`_.

::

    # Download a sequence from GenBank
    ID="FJ981613.1"
    wget -O Influenza_HA.fa "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=${ID}&rettype=fasta"

Alternatively, you may also begin with a protein sequence. For
example, the following command will download the protein sequence
of the Influenza A virus's HA protein from `UniProt
<https://www.uniprot.org/>`_.

::

    # Download a protein sequence from UniProt
    ID="C3W5X2"
    wget -O Influenza_HA_protein.fa "https://www.uniprot.org/uniprotkb/${ID}.fasta"

-------------------------------------
Step 2. Evaluating the Given Sequence
-------------------------------------

Before starting optimization, let's evaluate the sequence. By setting
the ``--iterations`` option to ``0``, VaxPress will generate a
report presenting the properties and optimality measures of the
provided sequence, without making any changes to the original
sequence.

::

    # Evaluate the initial sequence
    vaxpress -i Influenza_HA.fa -o eval_results --iterations 0

The output directory, ``eval_results``, will contain several data
files, including ``report.html``. Take a look at the sections on
*Sequence Optimality Metrics* and *Predicted Secondary Structure*
in the report. Since no optimization took place, the metrics of
the *Initial* and *Optimized* columns in the *Sequence Optimality
Metrics* section will be identical.

It's important to note that if the input is provided as a protein
sequence, the codons in the initial sequence will be chosen randomly.
As such, the evaluation results may not hold significant information
for the optimality of given protein sequence.

-------------------------------------
Step 3. Running VaxPress Optimization
-------------------------------------

.. index:: LinearDesign; tutorial

Let's proceed with the VaxPress optimization. With the ``--lineardesign``
option, VaxPress utilizes the sequence optimized by *LinearDesign* as
a starting point. *LinearDesign* produces a sequence with a virtually
minimum free energy secondary structure among all possible codon
combinations for the protein sequence. Subsequently, VaxPress performs even
further optimization based on all the other parameters. This includes
factors like start codon accessibility, GC content, tandem repeats,
and predicted in-cell and in-solution stability among others, along
with the already optimized secondary structure. See the
:ref:`using-lineardesign` for more details.

::

    # Run VaxPress optimization
    vaxpress -i Influenza_HA.fa -o vaxpress_results --processes 36 \
             --lineardesign 1.0 --lineardesign-dir path/to/LinearDesign \
             --conservative-start 10 --initial-mutation-rate 0.01 \
             --iterations 2000 --folding-engine linearfold

Using the ``--processes`` option is recommended to fully utilize
multiple CPU cores.  Also, employing the ``--folding-engine
linearfold`` can reduce the running time by a minimum of 50%, without
significant deterioration in optimization quality.

The final optimized sequence can be reviewed in the ``report.html``
found in the output directory. This document includes informative
sections such as *Sequence Optimality Metrics* and *Predicted
Secondary Structure.* The *Optimization Process* plots also help
diagnose and improve the optimization process.  If necessary,
optimization parameters can be modified based on these plots following
the :ref:`guide <tuning-parameters>` in this documentation.
