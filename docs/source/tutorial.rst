VaxPress Tutorial
*********************

This tutorial will walk you through the process of optimizing a wild-type mRNA sequence with VaxPress.
We will use Hemagglutinin(HA) protein of Influenza A virus as an example antigen.

--------------------------------
Step 1. Downloading a sequence
--------------------------------

Wild-type complete cds sequence can be downloaded from `GenBank <https://www.ncbi.nlm.nih.gov/genbank/>`_:
Particular GenBank page for the Influenza A virus HA protein is `here <https://www.ncbi.nlm.nih.gov/nuccore/FJ981613.1>`_. 
FASTA file can be downloaded from the above page, or using the command like below:
::
    # Download a sequence from GenBank
    $ ID="FJ981613.1"
    $ wget -O Influenza_HA.fa "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=${ID}&rettype=fasta"

If you want to download other sequences, run the above command after changing the ``ID`` variable to the GenBank Accession Number of that sequence.

`UniProt <https://www.uniprot.org/>`_ is a database for protein sequences. 
FASTA file can be downloaded from UniProt website by clicking the "Download" button in the query result page, 
or using wget command with primary accession number (See `UniProt - Programmatic access <https://www.uniprot.org/help/api_retrieve_entries>`_ for more details).
The corresponding protein sequence for the above HA sequence can be found `in here <https://www.uniprot.org/uniprotkb/C3W5X2/entry>`_.
::
    # Download a protein sequence from UniProt
    $ ID="C3W5X2"
    $ wget -O Influenza_HA_protein.fa https://www.uniprot.org/uniprotkb/${ID}.fasta

----------------------------------------
Step 2. Evaluating the initial sequence
----------------------------------------
Let's evaluate the sequence before any optimization.
By setting ``--iterations`` option to 0, VaxPress will only evaluate the given sequence and generate a report.
::
    # Evaluate the initial sequence
    $ vaxpress -i Influenza_HA.fa -o eval_results --iterations 0

This command will generate a report file named ``report.html`` inside the output directory.
Check the Sequence Optimality Metrics and Predicted Secondary Structure sections.
In this case, metrics of the Initial and Optimized in Sequence Optimality Metrics will be the same since there was no optimization.

-----------------------------------------------
Step 3. Running LinearDesign through VaxPress
-----------------------------------------------
This step runs LinearDesign optimization through VaxPress. If you're going to run VaxPress optimization as well, you can go directly to Step 4.

Assigning the same parameter for ``--conservative-start`` and ``--iterations`` options has the same effect as running LinearDesign optimization alone.
Keep in mind that LinearDesign is not installed automatically with VaxPress, so you need to install it separately. 
Give the path to the installed LinearDesign directory with ``--lineardesign-dir`` option.
::
    # Run LinearDesign optimization
    $ vaxpress -i Influenza_HA.fa -o lineardesign_results \
               --lineardesign 1.0 --lineardesign-dir ../LinearDesign \
               --conservative-start 10 --iterations 10

Check the ``report.html`` as in Step 2.
In this case, differences between "Initial" and "Optimized" sequence should be minimal, since the mutations were only allowed at the start codon region.

LAMBDA in ``--lineardesign LAMBDA`` option is a parameter to balance between MFE and CAI. Larger LAMBDA means more weights on CAI.

--------------------------------------
Step 4. Running VaxPress optimization
--------------------------------------
Finally, let's run VaxPress optimization, starting from the sequence optimized by LinearDesign.
::
    # Run VaxPress optimization
    $ vaxpress -i Influenza_HA.fa -o vaxpress_results --processes 36 \
               --lineardesign 1.0 --lineardesign-dir ../LinearDesign \
               --conservative-start 10 --initial-mutation-rate 0.01 \
               --iterations 2000


It is recommended to use ``-p`` or ``--processes`` option to make the runtime shorter.

If you're using a protein sequence, the only thing you have to do is adding ``--protein`` option.

Now you can see the optimized sequence in the ``report.html``.
In addition to the Sequence Optimality Metrics and Predicted Secondary Structure sections, plots in Optimization Process also contains useful information.
If needed, additional optimization parameters can be adjusted according to these plots and :doc:`the guide </guide_to_set_parameters>`.