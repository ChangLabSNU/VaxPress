Guide to set parameters
**************************

---------------------
Number of Iterations
---------------------
Number of iterations is a key parameter for genetic algorithm.
For a comprehensize optimization, high enough iteration number is needed. But unnecessarily high number of iteration higher than certain threshold occurs automatic shut down.

To have an output sequence sufficiently converged, at least 500 iterations are recommended.
It is recommended to increase the number of iterations if the optimization process ends before sufficient convergence.

Below is an example process with 500, 1000 and 1500 iterations on CDS sequence with the length of 1701 bp.
     
* Fitness changes over the iterations from ``report.html``
    1. 500 iterations
    
    .. image:: _images/iteration500.png
        :width: 500px
        :height: 350px
        :alt: iteration 500
        :align: center
    In this case, fitness score didn't reach plateau after 500 iterations, so it is recommended to increase the number of iterations.

    2. 1000 iterations
    
    .. image:: _images/iteration1000.png
        :width: 500px
        :height: 350px
        :alt: iteration 1000
        :align: center
    In this case, fitness score didn't reach plateau after 1000 iterations, so it is recommended to increase the number of iterations.

    3. 1500 iterations
    
    .. image:: _images/iteration1500.png
        :width: 500px
        :height: 350px
        :alt: iteration 1500
        :align: center
    Now we can opserve plateau at the end of the fitness score. So, you might select iteration number near 1500.
    Or if it's unsatisfactory for you to optimize, than use larger value for iteration number and check whether there are plateau or not.

Also, keep in mind that optimization process can halt before the specified number of iterations if the fitness score doesn't improve for several consecutive cycles.
In detail, if E(number of mutation) is equals to 0.2 because of decrease in mutation rate.

---------------------
Number of Population
---------------------
Number of population is one of the key parameters for genetic algorithm.
Higher population number allows wider search per each iteration, 
but too high value will lead to unnecessary use of time and computational resources.
To adjust it, run VaxPress with random population numbers, and find proper value that makes no further difference.

* Fitness changes over the iterations from ``report.html``
    1. 10 populations
    
    .. image:: _images/population10.png
        :width: 500px
        :height: 350px
        :alt: offspring 10
        :align: center

    2. 100 populations
    
    .. image:: _images/population100.png
        :width: 500px
        :height: 350px
        :alt: offspring 100
        :align: center

    3. 1000 populations
    
    .. image:: _images/population500.png
        :width: 500px
        :height: 350px
        :alt: offspring 1000
        :align: center

Near 100 is proper since there are no differences after 100.

.. note::
    **CAUTION**

    These processes are influenced by other options i.e. iteration number, survivor number…
    All of the parameters above except the population number is set to the default which is REALLY small.
    Other parameters can be adjusted as well based on your own purpose.

----------------------
Initial Mutation Rate
----------------------
To accomplish optimization successfully, certain amount of mutation rate is necessory.

When running *Vaxpress* without LinearDesign initialization, using default value for initial mutation rate (0.1) won't be a problem since the evolution starts from the highly unoptimized sequence.
When initial mutation rate is high, the program will search through the sequence space more widely, but more iterations might be needed for convergence.
If you set the initial mutation rate too low, VaxPress might lose the opportunity to find a better-scoring sequence by chance.

But if you initialize sequence with LinearDesign before VaxPress optimization, it is recommended to lower the initial mutation rate.
Since the output sequence from LinearDesign is already highly optimized, there is a minimal likelihood of more competitive populations to emerge under higher mutation rate.

Below is the example for adjusting initial mutation rate for the 2 cases.

++++++++++++++++++++++++++++++++++++
Case 1: LinearDesign is NOT applied
++++++++++++++++++++++++++++++++++++
* Fitness changes over the iterations from ``report.html``
    1. initial mutation rate = 0.005
        
    .. image:: _images/nonLD_mutRate0.005.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.005
        :align: center

    2. initial mutation rate = 0.01
        
    .. image:: _images/nonLD_mutRate0.01.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.01
        :align: center

    3. initial mutation rate = 0.1
        
    .. image:: _images/nonLD_mutRate0.1.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.1
        :align: center

    4. initial mutation rate = 0.3
        
    .. image:: _images/nonLD_mutRate0.3.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate 0.3
        :align: center

This is VaxPress optimization result starting from the wild-type CDS sequence of Influenza virus.
In this case, the final fitness score at convergence is not affected by initial mutation rate.
However, keep in mind that lower initial mutation rate might result in the optimization outcome to be stuck in the local optimum, although it generally allows the faster convergence.

++++++++++++++++++++++++++++++++++
Case 2: LinearDesign is applied
++++++++++++++++++++++++++++++++++
* Fitness changes over the iterations from ``report.html``
    1. initial mutation rate = 0.005
    
    .. image:: _images/LD1_mutRate0.005.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate = 0.005
        :align: center

    2. initial mutation rate = 0.01
        
    .. image:: _images/LD1_mutRate0.01.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate = 0.01
        :align: center

    3. initial mutation rate = 0.1
        
    .. image:: _images/LD1_mutRate0.1.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate = 0.1
        :align: center

    4. initial mutation rate = 0.3
        
    .. image:: _images/LD1_mutRate0.3.png
        :width: 500px
        :height: 350px
        :alt: initial mutation rate = 0.3
        :align: center
    
For the high initial mutation rate (0.1,0.3), the fitness score varies a lot with no trend. 
Also, for the low initial mutation rate (0.01,0.005), the lower the initial mutation rate, the higher the fitness score is.
Moreover, lower initial mutation rate (0.005) make faster improvement. 

Thus, low initial mutation rate is recommended when the initial sequence is already optimized with LinearDesign.
After setting iteration number, you might try initial mutation rate under 0.01 and observe the fitness score to set proper rate.

----------------------------------
Weights of the Fitness Functions
----------------------------------
The way of adjusting weights of fitness functions depends on the user’s own purpose.
To adjust the weights properly, you might refer to 4 steps in the example below.

.. note::
    Default weights of the fitness functions which are used in example sample are as follows:

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

    Elevation of *MFE* value is observed. Since *MFE* value represents overall stability of structure, you might want to make it lower.

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
    
    Now we have problem with the Uridine Count. Let’s compromise between ``loops`` and ``ucount``.

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
    
    Now ``loops`` and ``ucount`` are improved, but there is slight elevation of ``MFE``. So now there might be some possible choices.

    1. Take charge of slight elevation of `MFE`.
    2. Raise weight of `MFE` more.

    By doing the second choice, there might be several deteriorations of some other metrics.
    You can keep adjusting them just like the above process. How to balance the weights among the various fitness functions depends on your own purpose for using Vaxpress.