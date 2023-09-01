Optimization Options
*************************************

Below is the list of all arguments related to optimization parameters of the program.
Examples showing the effect of each parameters on the optimization process can be found in the :doc:`Guide to set parameters </guide_to_set_parameters>` section.

- ``--iterations`` N

  - number of iterations (default: 10)
- ``--offsprings`` N

  - number of offsprings per iteration (default: 20)
- ``--survivors`` N

  - number of survivors per iteration (default: 2)
- ``--initial-mutation-rate`` RATE

  - initial mutation rate (default: 0.1)
- ``--winddown-trigger`` N

  - number of iterations with the same best score to trigger mutation stabilization (default: 15)
- ``--winddown-rate`` RATE

  - mutation rate multiplier when mutation stabilization is triggered (default: 0.9)