Algorithmic Details of VaxPress
********************************
-----------------
Overall algorithm
-----------------
Vaxpress uses genetic algorithm to produce optimized mRNA cds sequence, while fitness evaluation metrics are defined as scoring functions. 

Current scoring functions consider both the features involved in the production and distribution process, as well as features affecting the efficacy *in vivo* such as immunogenecity and translational efficiency.
Third-party scoring functions can also be incorporated into the optimization process.

If the input sequence is a protein, it will first be backtranslated into an RNA sequence. 
The optimization process involves generating a population of RNA sequences with random mutations, 
evaluating these sequences using scoring functions, selecting survivor sequences, and repeating this process for a specified number of iterations.

.. image:: path/to/image.png
    :height: 250
    :width: 250
    :scale: 50
    :alt: Genetic algorithm used in vaxpress. 



-------------------------------
Composition of Scoring Function
-------------------------------

Vaxpress' scoring function consists of three main areas, each considering factors that can influence the optimization result:

====================
1. Codon Usage
====================

Codon usage bias, the frequency difference of synonymous codons in a coding sequence, significantly affects mRNA stability and protein production. Vaxpress aims to recommend sequences for mRNA vaccine development by reflecting the actual *in vivo* frequency of codon usage. This area includes:

- **CAI (Codon Adaptation Index):** A measure of codon usage bias that calculates the similarity between the test sequence's synonymous codon usage and a reference sequence's codon frequency. It uses the relative adaptiveness of codons to compute a score.

- **Bicodon Usage:** Considers the frequency of consecutive codon occurrences and calculates scores based on codon pairs.

In addition, Vaxpress obtains raw data of codon RSCU values and codon pair scores from the CoCoPUTs codon usage database.

.. image:: path/to/image.png
    :height: 250
    :width: 250
    :scale: 50
    :alt: bicodon usage.

====================
2. RNA Folding
====================

For stable mRNA vaccine development, RNA structural stability is crucial. Vaxpress incorporates scoring factors related to RNA folding, including:

- **MFE (Minimum Free Energy):** Represents the free energy of the most stable RNA structure. Vaxpress uses folding engines such as ViennaRNA and LinearFold to calculate MFE values.

- **Start Codon Structure:** Measures the length of the stem-loop structure near the start codon.

- **Loop (Unfolded) Length:** Considers the lengths of segments with unfolded loop structures.

- **Stem Length:** Considers the length of the stem region to prevent immune responses.

.. image:: path/to/image.png
    :height: 250
    :width: 250
    :scale: 50
    :alt: stem length.

===========================
3. Sequential Features
===========================

This area includes various factors that influence RNA sequence stability and immunogenicity, such as:

- **iCodon-Predicted Stability:** Predicts the stability of RNA secondary structure using synonymous codons.

- **Local GC Ratio:** Calculates the GC ratio within a window and transforms it into a score.

- **U Count:** Counts uridines in the sequence to minimize immune response.

- **Repeat Length:** Quantifies tandem repeat lengths to facilitate cloning for vaccine production.

---------------------------------------
Scoring Function (Objective Function)
---------------------------------------

The scoring function is a linear combination of the factors mentioned above, with associated weights. It is represented as follows:

Scoring Function = Σ(factors * weights)

-----------
References
-----------

1. Sharp, Paul M., and Wen-Hsiung Li. "The codon adaptation index-a measure of directional synonymous codon usage bias, and its potential applications." Nucleic acids research 15.3 (1987): 1281-1295.

2. Presnyak, Vladimir, et al. "Codon optimality is a major determinant of mRNA stability." Cell 160.6 (2015): 1111-1124.

3. Alexaki, Aikaterini, et al. "Codon and codon-pair usage tables (CoCoPUTs): facilitating genetic variation analyses and recombinant gene design." Journal of molecular biology 431.13 (2019): 2434-2441.

4. Zuker, Michael, and Patrick Stiegler. "Optimal computer folding of large RNA sequences using thermodynamics and auxiliary information." Nucleic acids research 9.1 (1981): 133-148.

5. Hofacker, Ivo L. "Energy-directed RNA structure prediction." RNA Sequence, Structure, and Function: Computational and Bioinformatic Methods (2014): 71-84.

6. Mauger, David M., et al. "mRNA structure regulates protein expression through changes in functional half-life." Proceedings of the National Academy of Sciences 116.48 (2019): 24075-24083.

7. Kearse, Michael G., et al. "Ribosome queuing enables non-AUG translation to be resistant to multiple protein synthesis inhibitors." Genes & development 33.13-14 (2019): 871-885.

8. Tinoco Jr, Ignacio, and Carlos Bustamante. "How RNA folds." Journal of molecular biology 293.2 (1999): 271-281.

9. Turner, Douglas H., and David H. Mathews. "NNDB: the nearest neighbor parameter database for predicting stability of nucleic acid secondary structure." Nucleic acids research 38.suppl_1 (2010): D280-D282.

10. Berke, Ian C., and Yorgo Modis. "MDA5 cooperatively forms dimers and ATP‐sensitive filaments upon binding double‐stranded RNA." The EMBO journal 31.7 (2012): 1714-1726