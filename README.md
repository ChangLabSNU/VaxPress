# VaxPress

VaxPress is a codon optimizer platform tailored for mRNA vaccine
development. It refines coding sequences starting from protein or
RNA sequences to boost both storage stability and *in vivo* protein
expression. Plus, additional properties can be easily programmed
into the optimization process with just a few lines of code via a
pluggable interface. For the detailed information about VaxPress,
including its options and algorithmic features, please refer to the
[VaxPress documentation page](https://vaxpress.readthedocs.io/).

# Installation

### pip

You can install VaxPress via pip.

#### Installing

```bash
# Create a virtual environment for VaxPress
python -m venv /path/to/vaxpress-env

# Activate the virtual environment
source /path/to/vaxpress-env/bin/activate

# Install VaxPress alone
pip install vaxpress

# Alternatively, install VaxPress with LinearFold (only for non-commercial uses)
pip install 'vaxpress[nonfree]'
```

#### Running

```bash
# Activate the virtual environment
source /path/to/vaxpress-env/bin/activate

# Run VaxPress
vaxpress -h
```

#### iCodon Dependency

If you wish to activate the iCodon predicted stability
(`--iCodon-weight`) in the fitness function, ensure you have
working installations of *R,* *rpy2* (version >= 3.0) and
*iCodon.*  For detailed installation instructions, visit
[iCodon's GitHub page](https://github.com/santiago1234/iCodon/).

### Conda

Alternatively, you may also install VaxPress via a conda package:

#### Installation

```bash
conda create -n vaxpress -y -c changlabsnu -c bioconda -c conda-forge vaxpress
```

#### Running

```bash
# Activate the environment
conda activate vaxpress

# Run VaxPress
vaxpress -h
```

### Singularity

To run VaxPress via Singularity, you will need to install the
[Singularity CE](https://sylabs.io/singularity/) first.
Download the container image from
[the GitHub project page](https://github.com/ChangLabSNU/VaxPress/releases)
and place it in a directory of your choice.

```bash
singularity vaxpress.sif -h
```

When using the Singularity image, both the input and output must
be somewhere inside your home directory for VaxPress to run without
complicated directory binding configurations for Singularity.

# Usage

## Quick Start

Here's a basic command-line instruction to start using VaxPress.
Note that `-i` and `-o` options are mandatory:

```bash
vaxpress -i spike.fa -o output --iterations 1000 -p 32
```

### Input

VaxPress requires a FASTA format input file that contains the CDS
(CoDing Sequence) to be optimized. In case the FASTA file holds a
protein sequence, the additional `--protein` switch is required.

### Number of Iterations

The `--iterations` option is set to `10` by default. However,
for thorough optimization, it's recommended to use at least `500`
iterations. The optimal number of iterations may differ depending
on the length, composition of the input, and the selected optimization
settings. It's important to note that the optimization process may
stop before completing all the specified iterations if no progress
is observed over several consecutive cycles. Guidelines for setting
the appropriate number of iterations and other optimization parameters
can be found in the
[Tuning Optimization Parameters](https://vaxpress.readthedocs.io/en/latest/user_guides.html#tuning-parameters)
section.

You can set `--iterations` to `0` to generate VaxPress's sequence
evaluation report without any optimization.

### Multi-Core Support

You can use multiple CPU cores for optimization with the `-p` or
`--processes` option.

### More About Options

VaxPress offers the flexibility to adjust optimization strategies
in detail and integrate with LinearDesign. It also allows several
more convenient functions such as preset parameters, user-defined
custom scoring functions, and etc. For comprehensive explanation,
please refer to [the manual](https://vaxpress.readthedocs.io/en/latest/).

## Output

Once you've run VaxPress, the specified output directory will contain
the following five files:

- ``report.html``: A summary report detailing the result and
  optimization process.
- ``best-sequence.fasta``: The refined coding sequence.
- ``checkpoints.tsv``: The best sequences and the evaluation results
  at each iteration.
- ``log.txt``: Contains the logs that were displayed in the console.
- ``parameters.json``: Contains the parameters employed for the optimization.
  This file can be feeded to VaxPress with the `--preset` option to duplicate
  the set-up for other sequence.

# Citing VaxPress

If you employed our software in your research, please
kindly reference our publication:

Ju, Ku, and Chang (2023) Title. Journal. Volume. (in preparation)

# License

VaxPress is distributed under the terms of the [MIT License](LICENSE.txt).

LinearFold and LinearDesign are licensed for non-commercial use
only. If considering commercial use, be cautious about using options
such as `--lineardesign` and `--folding-engine linearfold`.
