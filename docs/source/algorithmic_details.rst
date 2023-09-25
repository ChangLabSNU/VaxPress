******************
How VaxPress Works
******************

------------
Optimization
------------

.. index:: Genetic Algorithm

VaxPress uses genetic algorithm to produce optimized mRNA cds
sequence, while fitness evaluation metrics are defined as scoring
functions. Current scoring functions consider both the features
involved in the production and distribution process, as well as
features affecting the efficacy *in vivo* such as immunogenecity
and translational efficiency.

If the input sequence is a protein, it will first be backtranslated
into an RNA sequence. The initial population of RNA sequences
generates randomly mutated child sequences, up to a certain
number of children specified as ``--population``. These sequences
are then evaluated using scoring functions.  Based on the evaluation
results, a selection process is carried out to choose survivor
sequences, with the number of survivors specified as ``--survivors``.
From the chosen survivor sequences, new offspring sequences are
produced once again. This iterative process is repeated for a
certain number of iterations specified as ``--iterations``.

.. image:: _images/figure1.png
    :width: 500px
    :align: center
    :alt: Overview of the genetic algorithm used in VaxPress.


------------------
Objective Function
------------------

The objective function is a linear combination of the factors below,
with associated weights. It is represented as follows:

.. math:: Scoring \, Function =  \Sigma_{f \in factors} f*weight

Refer to the :doc:`scoring_functions` section for more details on
each factor.

.. index:: Winddown Trigger, Winddown Rate
.. _label_WinddownTR:

----------------------------
Winddown Trigger and Rate
----------------------------

To improve optimization performance, it is crucial to create new
populations that can compete effectively with previous generations.
As the optimization process progresses, highly mutated new populations
are less likely to be selected because the earlier sequences are
already well-optimized. Therefore, if the current fitness score
remains at a certain level even as optimization continues, it is
necessary to *winddown* the mutation rate. In VaxPress, the Winddown
Trigger represents the number of iterations with the same fitness
score required to decrease the mutation rate, and the Winddown Rate
is the factor by which the mutation rate is multiplied when the
winddown is triggered.
