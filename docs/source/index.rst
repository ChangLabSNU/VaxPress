Welcome to VaxPress's documentation!
************************************

VaxPress is a codon optimizer platform tailored for mRNA vaccine development. 
It refines coding sequences starting from protein or RNA sequences to boost both storage stability and in vivo protein expression. 
Plus, additional properties can be easily programmed into the optimization process with just a few lines of code via a pluggable interface.

--------------
Installation
--------------
Vaxpress can be installed with ``pip``, ``conda``, or ``singularity``.
Pip is simple and easy to use since it can be operated in single command line, but ``R``, ``rpy2`` and ``iCodon`` dependencies should be managed separately.
Using conda package also allows the installation with single command line, and all the dependencies will managed automatically in this case. But it'll be quite slow compared to other ways.
Lastly, Singularity is fast, and automatically manages all dependencies. But Singularity should be installed first.
Based on your own circumstance, select proper way to install Vaxrpess!

=====================================
1. Installing VaxPress via ``pip``
=====================================

.. note::
    **prerequisites**

    If you install VaxPress via pip, ``R``, ``rpy2`` (version >= 3.0) and ``iCodon`` aren't included as dependencies.
    If you want to utilize iCodon's predicted stability in the fitness function, you'll need to install these separately.
    For iCodon installation, see `iCodon's GitHub page <https://github.com/santiago1234/iCodon/>`_.

**Installation**
::
    # To install using pip
    pip install vaxpress

    # To install using pip with LinearFold (only for non-commercial uses)
    pip install 'vaxpress[nonfree]'

    # To install from the Github
    git clone https://github.com/ChangLabSNU/VaxPress.git
    cd VaxPress
    pip install .

==============================================
2. Installing Vaxpress via ``conda`` package
==============================================
**Installation**
::
    conda install -c changlabsnu -c bioconda -c conda-forge vaxpress

===========================================
3. Installing Vaxpress via ``Singularity``
===========================================
.. note::
    **prerequisite**

    To install VaxPress via Singularity, you will need to install `Singularity CE <https://sylabs.io/singularity/>`_ first.

**Installation**
Once Singularity is installed, you can download the VaxPress image from this GitHub repository and run using the following command:
::
    singularity vaxpress.sif ...

It is recommended that VaxPress be installed in a virtual environment to be controlled properly.
See `the python documentation for preparing virtual environments <https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/>`_

============================
Installing ``LinearDesign``
============================

To use ``--lineardesign`` options, ``LinearDesign`` installation is required apart from VaxPress installation.
You can follow the instructions on the LinearDesign's `LinearDesign GitHub Page <https://github.com/LinearDesignSoftware/LinearDesign>`_.


--------------
Basic Usage
--------------
There are 2 required arguments to run VaxPress: ``-i``, ``-o``.
``-i`` specifies the input file path, and ``-o`` specifies the output directory path.

Command-line below is an example of basic VaxPress usage. You might follow it:
::
    # To see a full list of available options, use vaxpress --help 
    vaxpress -h
   
    # Example command to run VaxPress
    # Specify input file, output directory, number of iterations, and number of processes to use 
    vaxpress -i {path_to_input.fa} -o {path_to_output_directory} --iterations {n_iterations} -p {n_processes}

==============
Input Files
==============
VaxPress requires an input file in FASTA format containing the CDS(CoDing Sequence) sequence to be optimized.
Protein sequence in FASTA format is also available as an input, using ``--protein`` option.


======================
Number of Iterations
======================
By default, the ``--iterations`` option is set to 10.
For a comprehensive optimization, it's suggested to use a minimum of 500 iterations.
However, the ideal number of iterations can vary based on the input's length, composition, and chosen optimization settings.
Note that the optimization process might halt before completing all specified iterations if no improvement is detected over several consecutive cycles.
Guide to set the appropriate iteration numbers and other optimization parameters can be found in :doc:`guide to set parameters </guide_to_set_parameters>` section.

=====================
Multi-Core Support
=====================
You can use multiple CPU cores for optimization with the ``-p`` or ``--processes`` option.
By default, VaxPress uses only one core. 
Adding ``--processes N`` option paralellizes the calculation needed for the scoring functions and secondary structure prediction in each iteration.
Assigning more cores will speed up the optimization process, as ``N`` specifies the maximum number of cores that the calculation can be distributed. 
However, suitable number of cores depends on the amount of available computational resources.


======================================
Adjusting the Fitness Scoring Scheme
======================================
VaxPress optimizes synonymous codon selections to potentially enhance the fitness of coding sequences for mRNA vaccines.
This fitness is derived from a cumulative score of various metrics, including the codon adaptation index, GC ratio, among others.
To emphasize or de-emphasize a specific feature, simply adjust its weight.

To fine-tune the optimization, adjust the weights of individual scoring functions using the ``--{func}-weight`` option. Setting a function's weight to ``0`` effectively disables it.

.. code-block:: bash

    # Concentrate on the stable secondary structure (more weight to the MFE)
    vaxpress -i spike.fa -o result-spike --mfe-weights 10

    # Turn off the consideration of repeated sequences
    vaxpress -i spike.fa -o result-spike --repeats-weight 0

VaxPress allows users to add their custom scoring functions. See :doc:`adding custom scoring functions </adding_scorefunc>` section.

A deeper understanding of the scoring functions' principles is available on the :doc:`Algorithmic Details </algorithmic_details>` section.


=====================================================
Using LinearDesign for Optimization Initialization
=====================================================
`LinearDesign <https://github.com/LinearDesignSoftware/LinearDesign>`_(Zhang et al., 2023) offers ultra-fast optimization, focusing on near-optimal MFE and CAI values. 
By using the ``--lineardesign`` option, VaxPress invokes LinearDesign internally then begins its optimization with a sequence already refined by LinearDesign.
Subsequent VaxPress optimizations further improves the sequences for features like secondary structures near the start codon, uridine count, in-cell stability, tandem repeats, and local GC content.

To start *VaxPress* optimization from LinearDesign output sequence, you can use ``--lineardesign`` option inside VaxPress. 
Path to the installed directory of LinearDesign should be provided using the ``--lineardesign-dir`` option. This option can be omitted in subsequent uses.
::
    # Running VaxPress with LinearDesign
    vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 500 --lineardesign 1.0 \
         --lineardesign-dir /path/to/LinearDesign \
         --conservative-start 10 --initial-mutation-rate 0.01

For detailed explanation of the recommended parameters when using ``--lineardesign`` option, see :doc:`Using LinearDesign for Optimization Initialization </running_with_lineardesign>` section.


==============
Output Files
==============
Once you've run VaxPress, the specified output directory will contain the following five files:

- ``report.html``: A summary report detailing the result and optimization process. The report contains the following informations:
  1. Basic information on the task including sequence name and command line.
  
  ..image:: _images/task_information.png
        :width: 500px
        :height: 400px
        :alt: checkpoints.tsv
        :align: center

  2. Information about the optimized sequence: metric comparison between initial & optimized score
  
  ..image:: _images/optimized_sequence.png
        :width: 500px
        :height: 400px
        :alt: checkpoints.tsv
        :align: center


  3. Interactive plot showing the predicted secondary structure of the output sequence
   
  ..image:: _images/predicted_secondary_structure.png
        :width: 500px
        :height: 400px
        :alt: checkpoints.tsv
        :align: center


  4. Plots showing the changes of each metrics and parameters over the iterations.
   
  ..image:: _images/optimization_process.png
        :width: 500px
        :height: 400px
        :alt: checkpoints.tsv
        :align: center


  5. Parameters used in the corresponding VaxPress run. This information is also stored in ``parameters.json``.
   
  ..image:: _images/parameters.png
        :width: 500px
        :height: 400px
        :alt: checkpoints.tsv
        :align: center

- ``best-sequence.fasta``:  The refined coding sequence.

- ``checkpoints.tsv``: The best sequences and its evaluation results at each iteration.
  .. image:: _images/checkpoints.tsv_example.png
        :width: 500px
        :height: 400px
        :alt: checkpoints.tsv
        :align: center

- ``log.txt``: Contains the logs that were displayed in the console.

- ``parameters.json``: Contains the parameters employed for the optimization. This file can be feeded to VaxPress with the ``--preset`` :ref:`option <label_name>` to duplicate the set-up for other sequence.
  (뒤에 preset 사용 방법 상세히 쓴 페이지 링크)


---------------
Tutorial
---------------

This tutorial will walk you through the process of optimizing a wild-type mRNA sequence with VaxPress.
We will use Hemagglutinin(HA) protein of Influenza A virus as an example antigen.

=======================================
Step 1. Downloading a sequence
=======================================

Wild-type complete cds sequence can be downloaded from `GenBank <https://www.ncbi.nlm.nih.gov/genbank/>`_:
Particular GenBank page for the Influenza A virus HA protein is `here <https://www.ncbi.nlm.nih.gov/nuccore/FJ981613.1>`_. 
FASTA file can be downloaded from the above page, or using the command like below:
::
    # Download a sequence from GenBank
    ID="FJ981613.1"
    wget -O Influenza_HA.fa "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id=${ID}&rettype=fasta"

If you want to download other sequences, run the above command after changing the ``ID`` variable to the GenBank Accession Number of that sequence.

`UniProt <https://www.uniprot.org/>`_ is a database for protein sequences. 
FASTA file can be downloaded from UniProt website by clicking the "Download" button in the query result page, 
or using wget command with primary accession number (See `UniProt - Programmatic access <https://www.uniprot.org/help/api_retrieve_entries>`_ for more details).
The corresponding protein sequence for the above HA sequence can be found `in here <https://www.uniprot.org/uniprotkb/C3W5X2/entry>`_.
::
    # Download a protein sequence from UniProt
    ID="C3W5X2"
    wget -O Influenza_HA_protein.fa "https://www.uniprot.org/uniprotkb/${ID}.fasta"

=========================================
Step 2. Evaluating the initial sequence
=========================================
Let's evaluate the sequence before any optimization.
By setting ``--iterations`` option to 0, VaxPress will only evaluate the given sequence and generate a report.
::
    # Evaluate the initial sequence
    vaxpress -i Influenza_HA.fa -o eval_results --iterations 0

This command will generate a report file named ``report.html`` inside the output directory.
Check the *Sequence Optimality Metrics* and *Predicted Secondary Structure* sections.
In this case, metrics of the Initial and Optimized in Sequence Optimality Metrics will be the same since there was no optimization.

=======================================
Step 3. Running VaxPress optimization
=======================================
Finally, all processes that are needed to run Vaxpress is ready. Now let's run VaxPress optimization, starting from the sequence optimized by LinearDesign.
But before running, we are going to point out why we start from LinearDesign result.
LinearDesign(Zhang et al., 2023) is an ultra-fast tool for mRNA CDS optimization in terms of MFE(Minimum Free Energy) and CAI(Codon Adaptation Index).
Instead of searching through the vast space of randomized sequences, starting genetic algorithm from the LinearDesign output sequence which is highly optimized in MFE and CAI offers more efficient optimization.

(Zhang, He, et al. "Algorithm for optimized mRNA design improves stability and immunogenicity." Nature (2023): 1-3.)
::
    # Run VaxPress optimization
    $vaxpress -i Influenza_HA.fa -o vaxpress_results --processes 36 \
              --lineardesign 1.0 --lineardesign-dir ../LinearDesign \
              --conservative-start 10 --initial-mutation-rate 0.01 \
              --iterations 2000


It is recommended to use ``-p`` or ``--processes`` option to make the runtime shorter. If you're using a protein sequence, the only thing you have to do is adding ``--protein`` option.

Now you can see the optimized sequence in the ``report.html``.
In addition to the Sequence Optimality Metrics and Predicted Secondary Structure sections, plots in Optimization Process also contains useful information.
If needed, additional optimization parameters can be adjusted according to these plots and :doc:`the guide </guide_to_set_parameters>`.



-------------------------------------------------------
Usages, options, and algorithmic features of VaxPress 
-------------------------------------------------------
.. toctree::
   :maxdepth: 2

   usage
   troubleshooting
   tutorial
   algorithmic_details
   adding_scorefunc
   running_with_lineardesign
   options
   guide_to_set_parameters
 
   

------------------
Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`