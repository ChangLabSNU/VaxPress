Guide to set parameters
**************************

---------------------
Number of Iterations
---------------------

To have an output sequence sufficiently converged, at least 500 iterations are recommended.
It is recommended to increase the number of iterations if the optimization process ends before sufficient convergence.

Below is an example with 500, 1000, 1500 iterations on CDS sequence length 576 bp, 1701 bp, 2429 bp.

.. image:: _images/500_iterations.png
    :width: 200px
    :height: 100px
    :alt: alternate text
    :scale: 50 %
    :align: center
In this case, fitness score didn't reach plateau after 500 iterations, so it is recommended to increase the number of iterations.

.. image:: _images/1000_iterations.png
    :width: 200px
    :height: 100px
    :alt: alternate text
    :scale: 50 %
    :align: center
Sequence sufficiently converged after around 600 iterations.
Also, keep in mind that optimization process can halt before the specified number of iterations if the fitness score doesn't improve for several consecutive cycles.


---------------------
Number of Offsprings
---------------------
Figure below shows the effect of the number of offsprings on the optimization process.

.. image:: _images/offsprings.png
    :width: 200px
    :height: 100px
    :alt: alternate text
    :scale: 50 %
    :align: center


----------------------
Initial Mutation Rate
----------------------

.. image:: _images/initial_mutrates.png
    :width: 200px
    :height: 100px
    :alt: alternate text
    :scale: 50 %
    :align: center

----------------------------------
Weights of the Fitness Functions
----------------------------------
Default weight of the fitness functions are as follows:
- MFE: 3.0
- GC content: 1.0

Adjusting weights of the fitness functions is like comprimising between several metrics. ... 

When A weight is increased, optimization on B tends to be more difficult. ... 

Figure below shows when A goes up, B goes down. ... 
.. image:: _images/exmaple_on_metrics_move.png
    :width: 200px
    :height: 100px
    :alt: alternate text
    :scale: 50 %
    :align: center

