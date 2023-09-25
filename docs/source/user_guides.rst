***********
User Guides
***********

.. index:: LinearDesign; Usage
.. _using-lineardesign:

--------------------------------------------------------
Using LinearDesign for Optimization Initialization
--------------------------------------------------------

LinearDesign [#LinearDesign]_ optimizes mRNA CDS in terms of MFE and CAI values.
You can use ``--lineardesign`` option to start *VaxPress* optimization
from LinearDesign output sequence.  When using this option,
LinearDesign is invoked inside VaxPress to initialize the input
sequence.  Subsequent VaxPress optimizations further improves the
sequence for the additional features like secondary structures near
the start codon, uridine count, in-cell stability, tandem repeats,
and local GC content.

The ``--lineardesign`` option needs a LAMBDA(λ) parameter, which
influences the balance between MFE and CAI.  Values between 0.5 and
4 are usually suitable starting points.  For insights into the λ
value's implications, consult Zhang et al. (2023) [#LinearDesign]_.

Keep in mind that LinearDesign should be installed separately
following instructions in the `LinearDesign GitHub page
<https://github.com/LinearDesignSoftware/LinearDesign>`_.  Path to
the installed directory of LinearDesign should be provided using
the ``--lineardesign-dir`` option. This option can be omitted in
subsequent uses.

Note that sequences straight from LinearDesign often have suboptimal
structures around the start codon.  Under the high mutation rate
at the beginning, this causes the main sequence body to lose its
optimal MFE structure.  The ``-—conservative-start`` :ref:`option
<label-constart>` tackles this by focusing on the start codon region
before optimizing the rest.

Also, given that *LinearDesign*'s outputs are already quite optimal,
the ``--initial-mutation-rate`` can be reduced to ``0.01``.  This
ensures efficient optimization as there's a minimal likelihood that
a better mutation would emerge with a higher mutation rate.
::

    # Running VaxPress with LinearDesign
    vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 500 --lineardesign 1.0 \
         --lineardesign-dir /path/to/LinearDesign \
         --conservative-start 10 --initial-mutation-rate 0.01

.. Note::
    Figures below demonstrates the effect of initial mutation rate
    on optimization process when the starting sequence is optimized
    with LinearDesign (λ = 0).
    
    .. image:: _images/mutrate0.1.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.1
        :align: center

    When initial mutation rate is set as a default value (``0.1``),
    survivor sequence largely remains unchanged for initial several
    hundred iterations, until the mutation rate is sufficiently
    decreased by *winddown*.

    .. image:: _images/mutrate0.01.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.01
        :align: center

    When initial mutation rate is adjusted to ``0.01``, the sequence
    can escape from initial MFE-optimized sequence earlier to be
    further optimized based on the given *VaxPress* evaluation
    metrics.

To see the list of all options related to LinearDesign, see
:ref:`label-linopts`.

.. _tuning-parameters:

------------------------------
Tuning Optimization Parameters
------------------------------

.. index:: Setting Parameters; Iterations

====================
Number of Iterations
====================

Number of iterations is a key parameter for genetic algorithm.  For
a comprehensize optimization, high enough iteration number is needed.
But unnecessarily high number of iteration higher than certain
threshold occurs automatic shut down.

To have an output sequence sufficiently converged, at least 500
iterations are recommended.  It is recommended to increase the
number of iterations if the optimization process ends before
sufficient convergence.

Below is an example process with 1500 iterations on CDS sequence
with the length of 1701 bp.
     
* Fitness changes over the iterations from ``report.html``
    
    .. image:: _images/iteration1500.png
        :width: 500px
        :height: 350px
        :alt: iteration1500
        :align: center

Two dotted lines on the plot are the points which the number of
iterations are 500 and 1000 each. 500 and 1000 iterations points
are showing possibility of further improvement since fitness score
is not plateau and mutation rate can decrease more. But near 1500
iterations, fitness and mutation rate are less likely to imrpove
more. Thus, in this case, it is proper to say that near 1500
iterations is okay to get optimal result.

Also, keep in mind that optimization process can halt before the
specified number of iterations if the fitness score doesn't improve
for several consecutive cycles.  In detail, if E(number of mutation)
is equal to 0.2 because of decrease in mutation rate.

.. index:: Setting Parameters; Population

====================
Number of Population
====================

Number of population is one of the key parameters for genetic
algorithm.  Higher population number allows wider search per each
iteration, but too high value will lead to unnecessary use of time
and computational resources.  To adjust it, run VaxPress with random
population numbers, and find proper value that makes no further
difference.

* Fitness changes over the iterations from ``report.html``
    1. 10 populations
    
    .. image:: _images/population10.png
        :width: 700px
        :height: 250px
        :alt: population 10
        :align: center

    2. 100 populations
    
    .. image:: _images/population100.png
        :width: 700px
        :height: 250px
        :alt: population 100
        :align: center

    3. 500 populations
    
    .. image:: _images/population500.png
        :width: 700px
        :height: 250px
        :alt: population 1000
        :align: center

Near 100 is proper since there are no differences for the value
that fitness curve converges after 100.

.. note::
    **CAUTION**

    These processes are influenced by other options i.e. iteration
    number, survivor number… All of the parameters above except the
    population number is set to the default which is REALLY small.
    Other parameters can be adjusted as well based on your own
    purpose.

.. index:: Setting Parameters; Initial Mutation Rate

=====================
Initial Mutation Rate
=====================

To accomplish optimization successfully, certain amount of mutation
rate is necessory.

When running *Vaxpress* without *LinearDesign* initialization, using
default value for initial mutation rate (``0.1``) won't be a problem
since the evolution starts from the highly unoptimized sequence.
When initial mutation rate is high, the program will search through
the sequence space more widely, but more iterations might be needed
for convergence.  If you set the initial mutation rate too low,
*VaxPress* might lose the opportunity to find a better-scoring
sequence by chance.

But if you initialize sequence with *LinearDesign* before *VaxPress*
optimization, it is recommended to lower the initial mutation rate.
Since the output sequence from LinearDesign is already highly
optimized, there is a minimal likelihood of more competitive
populations to emerge under higher mutation rate.

Below is the example for adjusting initial mutation rate for the 2
cases.

++++++++++++++++++++++++++++++++++++
Case 1: LinearDesign is NOT applied
++++++++++++++++++++++++++++++++++++

* Fitness changes over the iterations from ``report.html``
    1. initial mutation rate = 0.005
        
    .. image:: _images/nonLD_mutRate0.005.png
        :width: 700px
        :height: 250px
        :alt: initial mutation rate 0.005
        :align: center

    2. initial mutation rate = 0.01
        
    .. image:: _images/nonLD_mutRate0.01.png
        :width: 700px
        :height: 250px
        :alt: initial mutation rate 0.01
        :align: center

    3. initial mutation rate = 0.1
        
    .. image:: _images/nonLD_mutRate0.1.png
        :width: 700px
        :height: 250px
        :alt: initial mutation rate 0.1
        :align: center

    4. initial mutation rate = 0.3
        
    .. image:: _images/nonLD_mutRate0.3.png
        :width: 700px
        :height: 250px
        :alt: initial mutation rate 0.3
        :align: center

This is *VaxPress* optimization result starting from the wild-type
CDS sequence of Influenza virus.  In this case, the final fitness
score at convergence is not affected by initial mutation rate.
However, keep in mind that lower initial mutation rate might result
in the optimization outcome to be stuck in the local optimum,
although it generally allows the faster convergence.

++++++++++++++++++++++++++++++++++
Case 2: LinearDesign is applied
++++++++++++++++++++++++++++++++++
* Fitness changes over the iterations from ``report.html``
    1. initial mutation rate = 0.005
    
    .. image:: _images/LD1_mutRate0.005.png
        :width: 700px
        :height: 250px
        :alt: initial mutation rate = 0.005
        :align: center

    2. initial mutation rate = 0.01
        
    .. image:: _images/LD1_mutRate0.01.png
        :width: 700px
        :height: 250px
        :alt: initial mutation rate = 0.01
        :align: center

    3. initial mutation rate = 0.1
        
    .. image:: _images/LD1_mutRate0.1.png
        :width: 700px
        :height: 250px
        :alt: initial mutation rate = 0.1
        :align: center

    4. initial mutation rate = 0.3

    .. image:: _images/LD1_mutRate0.3.png
        :width: 700px
        :height: 250px
        :alt: initial mutation rate = 0.3
        :align: center
    
When the initial mutation rate is set high (``0.1``, ``0.3``), the
fitness score starts to increase at later iteration cycles.  Also,
when the initial mutation rate is low (``0.01``, ``0.005``), the
lower the initial mutation rate, the faster improvement is.

Thus, low initial mutation rate is recommended when the initial
sequence is already optimized with *LinearDesign*.  After setting
iteration number, you might try initial mutation rate under ``0.01``
and observe the fitness score to set proper rate.

.. index:: Setting Parameters; Fitness Function Weights

================================
Weights of the Fitness Functions
================================

The way of adjusting weights of fitness functions depends on the
user’s own purpose.  To adjust the weights properly, you might refer
to 4 steps in the example below.

.. note::
    Default weights of the fitness functions which are used in
    example sample are as follows:

    - MFE: 3.0
    - U count: 3.0
    - loop weight: 1.5
  

1. Check the naive optimization process
    Firstly, just run VaxPress with deafult weights.
    ::

        # command line
        vaxpress -i input/fastaFile/directory/example.fa -o output/directory/ --iterations 50 -p 64
    
    * Metrics' trend from ``report.html``
    
    .. image:: _images/weightTuning1.png
        :width: 500px
        :height: 350px
        :alt: weight tuning 1st step
        :align: center

    Elevation of *MFE* value is observed. Since *MFE* value represents
    overall stability of structure, you might want to make it lower.

2. Adjusting MFE weight (``--mfe-weight``)
    Raise weight of MFE from defalut to 7.0
    ::

        # command line
        vaxpress -i ... -o ... --iterations 50 --mfe-weight 7 -p 64
    
    * Metrics' trend from ``report.html``
    
    .. image:: _images/weightTuning2.png
        :width: 500px
        :height: 350px
        :alt: weight tuning 2nd step
        :align: center
    
    Now loops has increased, and you might want to keep the loops from increasing.

3. Adjusting loop weight (``--loop-weight``)
    Raise weight of loop from defalut to 7.0
    ::

        # command line
        vaxpress -i ... -o ... --iterations 50 --mfe-weight 7 --loop-weight 7 -p 64
    
    * Metrics' Trend from ``report.html``
    
    .. image:: _images/weightTuning3.png
        :width: 500px
        :height: 350px
        :alt: weight tuning 3rd step
        :align: center
    
    Now we have problem with the Uridine Count. Let’s compromise
    between ``loops`` and ``ucount``.

4. Compromising between ``loops`` and ``ucount``
    Raise weight of Ucount weight to 5 and lower loop weight to 5
    ::

        # command line
        vaxpress -i ... -o ... --iterations 50 --mfe-weight 7 --loop-weight 5 --ucount-weight 5 -p 64
    
    * Metrics' Trend from ``report.html``

    .. image:: _images/weightTuning4.png
        :width: 500px
        :height: 350px
        :alt: weight tuning 4th step
        :align: center
    
    Now ``loops`` and ``ucount`` are improved, but there is slight
    elevation of ``MFE``. So now there might be some possible
    choices.

    1. Take charge of slight elevation of `MFE`.
    2. Raise weight of `MFE` more.

    By doing the second choice, there might be several deteriorations
    of some other metrics.  You can keep adjusting them just like
    the above process. How to balance the weights among the various
    fitness functions depends on your own purpose for using Vaxpress.

.. index:: LinearDesign; Use Case

==================================================
Removing Tandem Repeats from LindearDesign Output
==================================================

Overall, VaxPress can consist a workflow starting from LinearDesign
(See :ref:`Using LinearDesign for Optimization Initialization
<using-lineardesign>` section for detailed information about the
related options and parameters).  In this usage, VaxPress refines
the MFE- or CAI-optimized sequence from LinearDesign on the other
factors not considered in LinearDesign.

For example, *VaxPress* can remove tandem repeats from the LinearDesign
output.

mRNA manufacturing is a significant process of mRNA vaccine
development.  However, the presence of repeated sequences cause
severe difficulties in the manufacturing process.  As *LinearDesign*
algorithm doesn't consider repeats, the output sequence from
LinearDesign may contain repeated sequences.  Especially, when the
``lambda`` parameter is set high(which means high weight on CAI),
the occurence of tandem repeat is highly probable since the codon
with high CAI score is always favored.
::

    # Example command to get LinearDesign-VaxPress optimized sequence 
    # with tandem repeats removed
    # MFE weight is set high to preserve the LinearDesign-optimized secondary structure
    # High weight set on Tandem Repeats, while CAI weight is set minimal.
    vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 500 --lineardesign 1.0 \
         --lineardesign-dir /path/to/LinearDesign \
         --conservative-start 10 --initial-mutation-rate 0.01 \
         --default-off \
         --mfe-weight 10 --repeats-weight 10 --cai-weight 1 --gc-weight 3 \
         --start-str-weight 1

=============================================================
Using VaxPress as a User-friendly Interface to LinearDesign
=============================================================

Using ``--conservative-start N`` option only generates mutations
in the start codon region during the initial N number of iterations,
leaving the rest of the sequence as it is.  Therefore, by assigning
the same parameter for ``--conservative-start`` and ``--iterations``
options, VaxPress can be used as a convenient front-end interface
for LinearDesign optimization.

.. note::
    **CAUTION**

    This use case explains running LinearDesign optimization ALONE
    through VaxPress.  If you're going to run VaxPress optimization
    as well, you can go directly to :doc:`tour`, Step 3.  Information
    about using LinearDesign for VaxPress optimization initialization
    is also available in :ref:`lineardesign` section.


Using LinearDesign through VaxPress interface offers several advantages:

- LinearDesign can be run without Python Version 2 dependency in VaxPress.
- In addition to the optimized sequence output by *LinearDesign*,
  *VaxPress* offers a comprehensive output report that is helpful to
  understand the optimized sequence. Detailed information is provided,
  such as the visualization of secondary structure and the scores of
  various evaluation metrics.
- When using LinearDesign alone, several N-terminal amino acids
  should be manually removed before running the optimization to prevent
  folded structures in the start codon region. This process is run
  automatically in VaxPress with ``--lineardesign-omit-start`` (default
  = 5) option.
- While LinearDesign only accepts protein sequence, mRNA sequence
  can be directly used as an input in VaxPress.

.. code-block:: bash

    # Example usage of VaxPress as an interface to LinearDesign
    vaxpress -i spike.fa -o results-spike --processes 36 \
            --iterations 10 --lineardesign 1.0 \
            --conservative-start 10 --initial-mutation-rate 0.01 \
            --lineardesign-dir /path/to/LinearDesign \


Results will be displayed in ``report.html``.  In this case,
differences between "Initial" and "Optimized" sequence should be
minimal, since the mutations were only allowed at the start codon
region.

=============================
Evaluating the given sequence
=============================

By setting ``--iterations`` to ``0``, VaxPress provides a convenient
method to just evaluate a given sequence with no further optimization.
Output report will be generated containing all the results from
VaxPress's scoring functions, including the visualization of secondary
structure.



.. index:: Preset

--------------------------------------------------------
Using preset values
--------------------------------------------------------

VaxPress stores its configuration information of each run in
``parameters.json`` file, which is generated inside the output
directory.  With ``--preset`` option, you can use preset values in
this file as the configuration for the next optimization.  This
option allows convenient preservation of the arguments applied in
particular run, which later can be used to reproduce the optimization,
to share with other people, etc.

Example command to use preset values::

    vaxpress -i {path_to_input.fa} \
             -o {path_to_output_directory} \
             --preset {path_to_parameters.json}

If some of the options are specified along with ``--preset``, the
specified arguments including addons will override the preset values.
For example, if you want to generate 10 replicates with certain
optimization parameters, only ``--seed`` option is needed to be
changed.  In this case, you can load preset values with ``--preset``
option and override only ``--seed`` argument to simplify the command.

.. code-block:: bash

    # Simplified command line with --preset option
    vaxpress -i {path_to_input.fa} \
             -o {path_to_output_directory} \
             --preset {path_to_parameters.json} \
             --seed {NUMBER}


.. index:: Configuration
.. _label-configuration:

--------------------------------------------------------
Modifying the default configuration
--------------------------------------------------------

Besides using ``--preset`` option, default settings of VaxPress can
also be modified.

When you install VaxPress, ``.config/vaxpress/config.json`` file
is generated inside the user's home directory.  You can find the
location of this file with the command below.

.. code-block::

    python -c "import os; print(os.path.join(os.path.expanduser('~'), '.config', 'vaxpress', 'config.json'))"

As a default, only ``--lineardesign-dir`` option is automatically
saved to this ``config.json`` among all the arguments you have
passed.  If VaxPress had run with ``--lineardesign-dir`` option,
``config.json`` would be written as below.

.. code-block::

    {
      "lineardesign_dir": "/path/to/LinearDesign/"
    }

This configuration file can be edited manually to change the default
settings of VaxPress, such as default weights of each scoring
function.  For example, to turn off *iCodon-Predicted Stability*
function as default, modify ``config.json`` like the example below.

.. code-block::
    
    {
      "lineardesign_dir": "/path/to/LinearDesign/",
      "iCodon_weight": 0
    }

As shown in this example, '-' in the argument name should be replaced
with '_' in configuration.  After this modification, ``--iCodon-weight``
option will be set to ``0`` as default.


.. index:: Addons
.. _label-addon:

--------------------------------------------------------
Adding a custom scoring function
--------------------------------------------------------

You can extend VaxPress optimization algorithm by adding custom
scoring functions that contributes to the fitness evaluation of
each sequence.  Example codes showing templates for additional
scoring functions are in ``VaxPress/examples`` directory.  After
preparing a python code for the new scoring function, you can add
it to the optimization process with two ways:

====================================
Using a command line option 
====================================

Pass the path to the Python source file for the scoring function
as an argument of ``-—addon`` option.  If there are multiple scoring
functions to add, ``-—addon`` can be specified multiple times.
::
    
    # Example command to add homotrimer count to the fitness evaluation

    vaxpress -i ./testseq/vegfa.fa\
             -o ../test_run\
             --iterations 500\
             --lineardesign 1\
             --lineardesign-dir ../LinearDesign\
             --conservative-start 10:7\
			 --addon ./VaxPress/examples/count_homotrimers.py


========================================================
Adding source files to the scoring function directory
========================================================

If you're going to use the custom scoring function repeatedly,
writing command line option every time can be cumbersome.  In this
case, source file of the custom function can be copied to the
directory where the original scoring functions of VaxPress are
installed.  To do this, first you will need to find where the
``vaxpress`` scoring modules are installed. It can be done with the
command below.

.. code-block:: bash

    # Prints the path to the directory that contains VaxPress scoring functions.
    python -c "import vaxpress.scoring as s; print(s.__path__)"  

    # Copy your source file to the directory found above.
    cp {path/to/your/scoring_function.py} {path/to/vaxpress/scoring_functions}
    
In this way, you can add your own scoring function to VaxPress
optimization without specifying the command line option every time.


----------
References
----------

.. [#LinearDesign] Zhang, He, et al. "Algorithm for optimized mRNA design improves stability and immunogenicity." Nature (2023): 1-3.