Supported features 
************************

This page introduces the supported features available on VaxPress.

.. contents:: :local:


.. index:: LinearDesign; Usage
.. _using-lineardesign:

--------------------------------------------------------
Using LinearDesign for Optimization Initialization
--------------------------------------------------------


LinearDesign [1]_ optimizes mRNA CDS in terms of MFE and CAI values.
You can use ``--lineardesign`` option to start *VaxPress* optimization from LinearDesign output sequence. 
When using this option, LinearDesign is invoked inside VaxPress to initialize the input sequence.
Subsequent VaxPress optimizations further improves the sequence for the additional features like secondary structures near the start codon, uridine count, in-cell stability, tandem repeats, and local GC content.

The ``--lineardesign`` option needs a LAMBDA(λ) parameter, which influences the balance between MFE and CAI. 
Values between 0.5 and 4 are usually suitable starting points.
For insights into the λ value's implications, consult Zhang et al. (2023).

Keep in mind that LinearDesign should be installed separately following instructions in the `LinearDesign GitHub page <https://github.com/LinearDesignSoftware/LinearDesign>`_. 
Path to the installed directory of LinearDesign should be provided using the ``--lineardesign-dir`` option. This option can be omitted in subsequent uses.

Note that sequences straight from LinearDesign often have suboptimal structures around the start codon. 
Under the high mutation rate at the beginning, this causes the main sequence body to lose its optimal MFE structure. 
The ``-—conservative-start`` :ref:`option <label-constart>` tackles this by focusing on the start codon region before optimizing the rest. 

Also, given that *LinearDesign*'s outputs are already quite optimal, the ``--initial-mutation-rate`` can be reduced to ``0.01``. 
This ensures efficient optimization as there's a minimal likelihood that a better mutation would emerge with a higher mutation rate.
::

    # Running VaxPress with LinearDesign
    vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 500 --lineardesign 1.0 \
         --lineardesign-dir /path/to/LinearDesign \
         --conservative-start 10 --initial-mutation-rate 0.01

.. Note::
    Figures below demonstrates the effect of initial mutation rate on optimization process when the starting sequence is optimized with LinearDesign (λ = 0).
    
    .. image:: _images/mutrate0.1.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.1
        :align: center

    When initial mutation rate is set as a default value (``0.1``), survivor sequence largely remains unchanged for initial several hundred iterations, until the mutation rate is sufficiently decreased by *winddown*.

    .. image:: _images/mutrate0.01.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.01
        :align: center

    When initial mutation rate is adjusted to ``0.01``, the sequence can escape from initial MFE-optimized sequence earlier to be further optimized based on the given *VaxPress* evaluation metrics.

To see the list of all options related to LinearDesign, see :ref:`label-linopts`.


.. index:: Addons
.. _label-addon:

--------------------------------------------------------
Adding a custom scoring function
--------------------------------------------------------
You can extend VaxPress optimization algorithm by adding custom scoring functions that contributes to the fitness evaluation of each sequence. 
Example codes showing templates for additional scoring functions are in ``VaxPress/examples`` directory. 
After preparing a python code for the new scoring function, you can add it to the optimization process with two ways:  

====================================
Using a command line option 
====================================
Pass the path to the Python source file for the scoring function as an argument of ``-—addon`` option. 
If there are multiple scoring functions to add, ``-—addon`` can be specified multiple times.
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
If you're going to use the custom scoring function repeatedly, writing command line option every time can be cumbersome.
In this case, source file of the custom function can be copied to the directory where the original scoring functions of VaxPress are installed.
To do this, first you will need to find where the ``vaxpress`` scoring modules are installed. It can be done with the command below.

.. code-block:: bash

    # Prints the path to the directory that contains VaxPress scoring functions.
    python -c "import vaxpress.scoring as s; print(s.__path__)"  

    # Copy your source file to the directory found above.
    cp {path/to/your/scoring_function.py} {path/to/vaxpress/scoring_functions}
    
In this way, you can add your own scoring function to VaxPress optimization without specifying the command line option every time. 


.. index:: Preset

--------------------------------------------------------
Using preset values
--------------------------------------------------------

VaxPress stores its configuration information of each run in ``parameters.json`` file, which is generated inside the output directory.
With ``--preset`` option, you can use preset values in this file as the configuration for the next optimization.
This option allows convenient preservation of the arguments applied in particular run, 
which later can be used to reproduce the optimization, to share with other people, etc. 

Example command to use preset values::

    vaxpress -i {path_to_input.fa} \
             -o {path_to_output_directory} \
             --preset {path_to_parameters.json}

If some of the options are specified along with ``--preset``, the specified arguments including addons will override the preset values.
For example, if you want to generate 10 replicates with certain optimization parameters, only ``--seed`` option is needed to be changed.
In this case, you can load preset values with ``--preset`` option and override only ``--seed`` argument to simplify the command.

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

Besides using ``--preset`` option, default settings of VaxPress can also be modified.

When you install VaxPress, ``.config/vaxpress/config.json`` file is generated inside the user's home directory.
You can find the location of this file with the command below. 

.. code-block::

    python -c "import os; print(os.path.join(os.path.expanduser('~'), '.config', 'vaxpress', 'config.json'))"

As a default, only ``--lineardesign-dir`` option is automatically saved to this ``config.json`` among all the arguments you have passed.
If VaxPress had run with ``--lineardesign-dir`` option,  ``config.json`` would be written as below.

.. code-block::

    {
      "lineardesign_dir": "/path/to/LinearDesign/"
    }

This configuration file can be edited manually to change the default settings of VaxPress, such as default weights of each scoring function.
For example, to turn off *iCodon-Predicted Stability* function as default, modify ``config.json`` like the example below.

.. code-block::
    
    {
      "lineardesign_dir": "/path/to/LinearDesign/",
      "iCodon_weight": 0
    }

As shown in this example, '-' in the argument name should be replaced with '_' in configuration.
After this modification, ``--iCodon-weight`` option will be set to ``0`` as default.

-----------------------
References
-----------------------
.. [1] Zhang, He, et al. "Algorithm for optimized mRNA design improves stability and immunogenicity." Nature (2023): 1-3.