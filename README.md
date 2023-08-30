# VaxPress

# Introduction

*그림 첨부*

VaxPress is a powerful codon optimization tool designed specifically for mRNA vaccine development. Vaxpress uses genetic algorithm to optimize mRNA cds or protein sequence, while fitness evaluation metrics are defined as scoring functions.

Full documentation which includes detailed information about all the options and algorithmic features used in VaxPress is available on [Vaxpress documentation page](#Welcome_page).

# Installation

### pip

You can install VaxPress via pip:

```bash
# To install from PyPI package:
pip install vaxpress

# To install from github source:
git clone https://github.com/ChangLabSNU/VaxPress.git
cd ./VaxPress
pip install .
```

### conda
VaxPress conda package is also available:
```bash
conda install -c conda-forge -c bioconda -c changlabsnu vaxpress
```

### Singularity
First, you will need to install [Singularity CE](https://sylabs.io/singularity/). Once Singularity is installed, you can download the VaxPress image from this GitHub repository and run using the following command:

```bash
singularity vaxpress.sif ...
```


# Usage
## Quick Start
Basic command-line usage of vaxpress looks like below, with 2 required options(```-i```, ```-o```):
```bash
vaxpress -i {path_to_input.fa} -o {path_to_output_directory} --iterations {n_iterations} -p {n_processes}
```
### Input Files
-  mRNA cds sequence in fasta format. Protein sequence in fasta format is also available as an input using ```--protein``` option.
### Output Files
-  output directory will contain the following 5 files:
   -  ```best-sequence.fasta```: Optimized mRNA cds sequence.
   - ```checkpoints.tsv```: Stores the  best-scoring mRNA sequence and its scores on each objectives in each iteration.
   - ```log.txt```: Stores the program log displayed on terminal.
   - ```parameters.json```: Stores parameters used when running the optimization. You can load these parameter values directly into next optimization using ```--preset``` option.
   - ```report.html```: Optimization summary report.
### Iterations
Default value of ```--iterations``` option is set to 10. To have an output sequence sufficiently converged, at least 500 iterations are recommended. It is recommended to increase the number of iterations if the optimization process ends before sufficient convergence. Guide to set the appropriate iteration numbers and other optimization parameters can be found [here](#page).
### Multiprocessing
Multiprocessing is supported in VaxPress, with ```-p```, ```--processes``` option.

## Adjusting the scoring criteria
Current scoring functions consider both the features involved in the production and distribution process, as well as features affecting the efficacy *in vivo* such as immunogenecity and translational efficiency. Principles of all scoring functions in VaxPress is listed on [VaxPress optimization algorithm](#algorithm_page).

### Changing weights
You can change the evaluation criteria of the optimization by changing weights of the individual scoring functions with ```—{func}-weight``` option. Each scoring function can be practically turned off by setting ```—{func}-weight``` to 0.
```bash
# Example command to set mfe weights higher:
vaxpress -i ./testseq/vegfa.fa -o ../test_run --iterations 500 --folding-mfe-weights 10

# Example command to turn off the scoring based on repeats:
vaxpress -i ./testseq/vegfa.fa -o ../test_run --iterations 500 --repeats-weight 0
```

### Adding a third-party scoring function
In addition to the existing ones, you can add custom scoring functions that will be considered during the optimization using ```--addon``` option. For detailed information on how to add and use third-party scoring functions in VaxPress, please refer to [Adding a scoring function](#scoring_func) page.


## Starting from LinearDesign-optimized sequence
[LinearDesign](https://github.com/LinearDesignSoftware/LinearDesign)(He Zhang, Liang Zhang, Ang Lin, Congcong Xu et al., 2023) is another tool for codon optimization. While LinearDesign optimizes mRNA sequences based on MFE and CAI, Vaxpress can be used for further optimization of the LinearDesign output sequence since it takes more evaluation metrics into account such as ucount, iCodon-predicted stability and local GC ratio.

To start VaxPress optimization from LinearDesign output sequence, you can use ```--lineardesign``` option inside VaxPress. Before using the option, LinearDesign should be installed separately following instructions in the [github page](https://github.com/LinearDesignSoftware/LinearDesign). Installed path should be specified as an argument with ```--lineardesign-dir```.

Using ```—conservative-start``` option with ```--lineardesign``` is recommended to prevent initial de-optimization of MFE while trying to get rid of folding structures near the start codon. Adjusting ```--initial-mutation-rate``` down to 0.01 is also recommended, since higher initial mutation rate usually causes large MFE deterioration from the initial MFE-optimized LinearDesign output sequence, preventing the sequence from evolving.
```bash
#Example command to start optimization from lineardesign output sequence
vaxpress -i ./testseq/vegfa.fa\
         -o ../test_run\
         --iterations 500\
         --lineardesign 1\
         --lineardiesign-dir ../LinearDesign\
         --conservative-start 10[:7]
         --initial-mutation-rate 0.01
```


## License
This project is licensed under the MIT License.

## Contact
If you have any questions or feedback, please feel free to contact us.
*email_address*