# VaxPress

## Introduction

VaxPress is a powerful codon optimization tool designed specifically for mRNA vaccine development. It uses various biological factors such as iCodon stability, Codon Adaptation Index (CAI), U count minimization, RNA folding, GC ratio, and tandem repeats to optimize codon usage, aiming to enhance mRNA stability, translation efficiency, and immunogenicity. 

## Installation

### pip

You can install VaxPress via pip:

```bash
pip install vaxpress
```

### conda
```bash
conda install -c conda-forge -c bioconda -c changlabsnu vaxpress
```

### Singularity
First, you will need to install [Singularity CE](https://sylabs.io/singularity/). Once Singularity is installed, you can download the VaxPress image from our GitHub repository and run using the following command:

```bash
singularity vaxpress.sif ...
```

## Usage
```bash
vaxpress -i INPUT -o OUTPUT
```
For more detailed usage instructions including all the available options, please refer to the [usage guide](#usage-guide).

## Input/Output Options
These options include input fasta file, whether input is a protein sequence, output directory, etc.

## Execution Options
These options include preset values, number of processes, random seed, target species, etc.

## Optimization Options
These options include number of iterations, offsprings per iteration, survivors per iteration, initial mutation rate, etc.

## Fitness Options
These options include scoring weights for iCodon predicted stability, CAI, bicodon-weight, U count minimizer, RNA folding, GC ratio, tandem repeats, etc.

## License
This project is licensed under the MIT License.

## Contact
If you have any questions or feedback, please feel free to contact us.
