Guide to set parameters
**************************

---------------------
Number of Iterations
---------------------
Number of iterations is key factor for genetic algorithm.
To make fitness score high enough, iteration number is needed to be high. But massive number of iteration means waste of time.

Thus, to have an output sequence sufficiently converged, at least 500 iterations are recommended.
It is recommended to increase the number of iterations if the optimization process ends before sufficient convergence.

Below is an example process with 500, 1000, 1500 iterations on CDS sequence length 1701 bp.

* command line
    vaxpress -i /input/fastaFile/directory/example.fa -o output/directory/ --iterations ITERATION -p 64
    (ITERATION = 500,1000,1500)
     
* Fitness changes over the iterations from report.html
    1. 500 iterations
    
    .. image:: _images/iteration500.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center
    In this case, fitness score didn't reach plateau after 500 iterations, so it is recommended to increase the number of iterations.

    2. 1000 iterations
    
    .. image:: _images/iteration1000.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center
    In this case, fitness score didn't reach plateau after 1000 iterations, so it is recommended to increase the number of iterations.

    3. 1500 iterations
    
    .. image:: _images/iteration1500.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center
    Now we can opserve plateau at the end of the fitness score. So, you might select iteration number near 1500.
    Or if it's unsatisfactory for you to optimize, than use larger value for iteration number and check whether there are plateau or not.

Also, keep in mind that optimization process can halt before the specified number of iterations if the fitness score doesn't improve for several consecutive cycles.

---------------------
Number of Offsprings
---------------------
Number of offspring is one of the key factors for genetic algorithm. But too high value is going to make waste of time. 
To adjust it, run Vaxpress with random offspring numbers, and find proper value that makes no further difference.

Below is an example process with 10, 100, 1000 offsprings on CDS sequence length 1701 bp.

* command line
    vaxpress -i /input/fastaFile/directory/example.fa -o output/directory/ --offsprings OFFSPRING -p 64
    (OFFSPRING = 10,100,1000)
* Fitness changes over the iterations from report.html
    1. 10 offsprings
    
    .. image:: _images/offspring10.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    2. 100 offsprings
    
    .. image:: _images/offspring100.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    3. 1000 offsprings
    
    .. image:: _images/offspring1000.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

Near 100 is proper since there are no differences after 100.

**CAUTION**
 These processes are influenced by other options i.e. iteration number, survivor number… 
 All of the values above except offspring number is default. 
 You need to adjust other values on your own according to personal purpose.

----------------------
Initial Mutation Rate
----------------------
To accomplish genetic algorithm successfully, certain amount of mutation rate are necessory. 

For running Vaxpress without LinearDesign, Initial Mutation Rate might be not important since previous generations are highly unoptimized.
Thus, it is okay to run default mutation rate in the most cases. The only differences by change initial mutation rate from here will be the moment that fitness get converged.

But if you are applying LinearDesign before Vaxpress, you have to set initial mutation rate quite low. 
It's because result from LinearDesign is already optimized, so if the rate is too high, than there will be no competitive offsprings comparing to previous generation. 

Below is examples for adjust initial mutation rate for all cases.

**Case 1 : LinearDesign is NOT applied**

* command line
    vaxpress -i /input/fastaFile/directory/example.fa -o output/directory/ --initial-mutation-rate MUT_RATE -p 64 
    (MUT_RATE = 0.005,0.01,0.1,0.3)
* Fitness changes over the iterations from report.html
    1. initial mutation rate = 0.005
        
    .. image:: _images/nonLD_mutRate0.005.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    2. initial mutation rate = 0.01
        
    .. image:: _images/nonLD_mutRate0.01.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    3. initial mutation rate = 0.1
        
    .. image:: _images/nonLD_mutRate0.1.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    4. initial mutation rate = 0.3
        
    .. image:: _images/nonLD_mutRate0.3.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

The level of fitness score at convergence is not affected by initial mutation rate.
So for enough number of iteration, initial mutation rate is not important.

**Case 2 : LinearDesign is applied**

* command line
    vaxpress -i /input/fastaFile/directory/example.fa -o output/directory/ --initial-mutation-rate MUT_RATE --lineardesign 1 --lineardesign-dir /Directory/of/LinearDesign -p 64  
    (MUT_RATE = 0.005,0.01,0.1,0.3)
* Fitness changes over the iterations from report.html
    1. initial mutation rate = 0.005
    
    .. image:: _images/LD1_mutRate0.005.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    2. initial mutation rate = 0.01
        
    .. image:: _images/LD1_mutRate0.01.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    3. initial mutation rate = 0.1
        
    .. image:: _images/LD1_mutRate0.1.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    4. initial mutation rate = 0.3
        
    .. image:: _images/LD1_mutRate0.3.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center
    
For the high initial mutation rate(0.1,0.3), the fitness score varies a lot with no trend. 
Also, for the low initial mutation rate (0.01,0.005), the lower the initial mutation rate, the higher the fitness score is.
Moreover, lower initial mutation rate(0.005) make faster improvement. 

Thus, low initial mutation rate is recommended for the case of LinearDesign applied.
After setting iteration number, you might try initial mutation rate under 0.01 and observe the fitness score to set proper rate.

----------------------------------
Weights of the Fitness Functions
----------------------------------
Weights of many scoring functions are depending on user’s own purpose. 
To adjust them properly, you might refer to 4 steps below which are example for adjusting weights. 

**FYI**

Default weights of the fitness functions which are used in example sample are as follows:
- MFE: 3.0
- U count: 3.0
- loop weight: .15

1. Check Naive Optimizing Process
    Firstly, just run without any special options.
    
    * command line
        vaxpress -i input/fastaFile/directory/example.fa -o output/directory/ --iterations 50 -p 64
    * Metrics' Trend from `report.html`
    
    .. image:: _images/weightTuning1.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center

    There is elevation of `MFE` value. Since `MFE` value represents overall stability of structure, you might want to lower it.

2. Adjusting MFE weight (`--mfe-weight`)
    Raise weight of MFE from defalut to 7.0
    
    * command line
        vaxpress -i input/fastaFile/directory/example.fa -o output/directory/ --iterations 50 --mfe-weight 7 -p 64
    * Metrics' Trend from `report.html`
    
    .. image:: _images/weightTuning2.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center
    
    Now loops has increased, and you might want to keep the value low. 

3. Adjusting loop weight (`--loop-weight`)
    Raise weight of loop from defalut to 7.0
    
    * command line
        vaxpress -i input/fastaFile/directory/example.fa -o output/directory/ --iterations 50 --mfe-weight 7 --loop-weight 7 -p 64
    * Metrics' Trend from `report.html`
    
    .. image:: _images/weightTuning3.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center
    
    Now we have problem with `Ucount`. So let’s compromise between `loops` and `Ucount`.

4. Compromising between `loops` and `ucount`
    Raise weight of Ucount weight to 5 and lower loop weight to 5
    
    * command line
        vaxpress -i input/fastaFile/directory/example.fa -o output/directory/ --iterations 50 --mfe-weight 7 --loop-weight 5 --ucount-weight 5 -p 64
    * Metrics' Trend from `report.html`
    .. image:: _images/weightTuning4.png
        :width: 200px
        :height: 100px
        :alt: alternate text
        :scale: 50 %
        :align: center
    
    Now `loops` and `ucount` are improved, but there is slight elevation of `MFE`. So now there might be some possible choices.

    1. Take charge of slight elevation of `MFE`. 
    2. Raise weight of `MFE` more.

    By doing second choice, there might be several deteriorations for some other metrics.
    You can keep adjusting them just like above processes. It’s on your own purpose for using Vaxpress. 