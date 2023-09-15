Using LinearDesign for Optimization Initialization
***************************************************


-----------------------
Introduction
-----------------------

`LinearDesign <https://github.com/LinearDesignSoftware/LinearDesign>`_(Zhang et al., 2023) offers ultra-fast optimization, focusing on near-optimal MFE and CAI values. 
By using the ``--lineardesign`` option, VaxPress invokes LinearDesign internally then begins its optimization with a sequence already refined by LinearDesign.
Subsequent VaxPress optimizations further improves the sequences for features like secondary structures near the start codon, uridine count, in-cell stability, tandem repeats, and local GC content.

To start *VaxPress* optimization from LinearDesign output sequence, you can use ``--lineardesign`` option inside VaxPress. 
Before using the option, LinearDesign should be installed separately following instructions in the `LinearDesign GitHub page <https://github.com/LinearDesignSoftware/LinearDesign>`_. 
Path to the installed directory of LinearDesign should be provided using the ``--lineardesign-dir`` option. This option can be omitted in subsequent uses.

-----------------------
Recommended Parameters
-----------------------

The ``--lineardesign`` option needs a LAMBDA(λ) parameter, which influences the balance between MFE and CAI. 
Values between 0.5 and 4 are usually suitable starting points.
For insights into the λ value's implications, consult Zhang et al. (2023).

Note that sequences straight from LinearDesign often have suboptimal structures around the start codon. 
Under the high mutation rate at the beginning, this causes the main sequence body to lose its optimal MFE structure. 
The ``-—conservative-start`` :ref:`option <label_constart>` tackles this by focusing on the start codon region before optimizing the rest. 

Also, given that *LinearDesign*'s outputs are already quite optimal, the ``--initial-mutation-rate`` can be reduced to 0.01. 
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
    When initial mutation rate is set as a default value (0.1), survivor sequence largely remains unchanged for initial several hundred iterations, until the mutation rate is sufficiently decreased by winddown.
    
    .. image:: _images/mutrate0.01.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.01
        :align: center
    When initial mutation rate is adjusted to 0.01, the sequence can escape from initial MFE-optimized sequence earlier to be further optimized based on the given VaxPress evaluation metrics.

---------------------------------
List of all LinearDesign options
---------------------------------
- ``--lineardesign`` LAMBDA

  Call LinearDesign to initialize the optimization. LAMBDA (λ) is a parameter specifying the ratio that MFE and CAI are reflected in the optimization. λ is in (–∞, 0] while λ = 0 means only MFE is considered, and the weight on CAI increases as λ increases. 

- ``--lineardesign-dir`` DIR

  Path to the top directory containing LinearDesign.

- ``--lineardesign-omit-start`` AA

  The number of amino acids to omit from the N-terminus when calling LinearDesign (default: 5). By using this option, generation of folded structures in start codon region while optimizing MFE by LinearDesign can be avioded.