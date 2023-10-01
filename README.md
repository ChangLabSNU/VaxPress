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
vaxpress -i {path_to_input.fa} -o {path_to_output_directory} --iterations {n_iterations} -p {n_processes}
```

### Input

Provide a CDS sequence in FASTA format. Alternatively, if you have
a protein sequence in FASTA format, use the `--protein` option.

### Number of Iterations

By default, the `--iterations` option is set to 10.  For a comprehensive
optimization, it's suggested to use a minimum of 500 iterations.
However, the ideal number of iterations can vary based on the input's
length, composition, and chosen optimization settings. Note that
the optimization process might halt before completing all specified
iterations if no improvement is detected over several consecutive
cycles.

By setting the number of `--iterations` to 0, VaxPress provides a convenient
method to just evaluate a given sequence with its various scoring functions.

### Multi-Core Support

You can use multiple CPU cores for optimization with the `-p` or
`--processes` option.

## Adjusting the Fitness Scoring Scheme

VaxPress optimizes synonymous codon selections to potentially enhance
the fitness of coding sequences for mRNA vaccines. This fitness is
derived from a cumulative score of various metrics, including the
codon adaptation index, GC ratio, among others. To emphasize or
de-emphasize a specific feature, simply adjust its weight. A deeper
understanding of the scoring functions' principles is available on
the [documentation](https://vaxpress.readthedocs.io/en/latest/scoring_functions.html).

### Setting Weights

To fine-tune the optimization, adjust the weights of individual
scoring functions using the `--{func}-weight` option. Setting a
function's weight to `0` effectively disables it.

```bash
# Concentrate on the stable secondary structure (more weight to the MFE)
vaxpress -i spike.fa -o result-spike --mfe-weights 10

# Turn off the consideration of repeated sequences
vaxpress -i spike.fa -o result-spike --repeats-weight 0
```

### Custom Scoring Functions

VaxPress allows users to add their custom scoring functions. This
feature enables a more targeted optimization process by integrating
new sequence attributes of interest. For detailed instructions,
please refer to the [Adding a scoring function page](#scoring_func).

## Using LinearDesign for Optimization Initialization

[LinearDesign](https://github.com/LinearDesignSoftware/LinearDesign)
([Zhang *et al.,* 2023](https://www.nature.com/articles/s41586-023-06127-z)) offers ultra-fast optimization, focusing on
near-optimal MFE and CAI values. By using the `--lineardesign`
option, VaxPress invokes LinearDesign internally then begins its
optimization with a sequence already refined by LinearDesign.
Subsequent VaxPress optimizations further improves the sequences
for features like secondary structures near the start codon, uridine
count, in-cell stability, tandem repeats, and local GC content.

To utilize the LinearDesign integration, provide the path to the
installed directory of LinearDesign using the `--lineardesign-dir`
option. This option can be omitted in subsequent uses. The
`--lineardesign` option also needs a LAMBDA parameter, which influences
the balance between MFE and CAI. Values between 0.5 and 4 are usually
suitable starting points. For insights into the LAMBDA value's
implications, consult Zhang *et al.* (2023).

Note that sequences straight from LinearDesign often have suboptimal
structures around the start codon. Under the high mutation rate at
the beginning, this causes the main sequence body to lose its optimal
MFE structure. The `-—conservative-start` option tackles this by
focusing on the start codon region before optimizing the rest. Also,
given that LinearDesign's outputs are already quite optimal, the
`--initial-mutation-rate` can be reduced to 0.01.  This ensures
efficient optimization as there's a minimal likelihood that a better
mutation would emerge with a higher mutation rate.

```bash
# Running VaxPress with LinearDesign
vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 500 --lineardesign 1.0 \
         --lineardesign-dir /path/to/LinearDesign \
         --conservative-start 10 --initial-mutation-rate 0.01
```
### Using VaxPress as a User-friendly Interface to LinearDesign
Using `--conservative-start N` option only generates mutations in
the start codon region during the initial N number of iterations,
leaving the rest of the sequence as it is. Therefore, by assigning
the same parameter for `--conservative-start` and `--iterations` options,
VaxPress can be used as a convenient front-end interface for
LinearDesign optimization.

Using LinearDesign through VaxPress interface offers several advantages:

- LinearDesign can be run without python2 dependency in VaxPress.
- In addition to the optimized sequence output by LinearDesign,
  VaxPress produces output report that contains detailed information
  about the sequence including the visualization of secondary structure
  and evaluation results of various metrics.
- When using LinearDesign alone, several N-terminal amino acids should
  be manually removed before running the optimization to prevent folded
  structures in the start codon region. This process is run automatically
  in VaxPress with `--lineardesign-omit-start`(default = 5) option.
- While LinearDesign only accepts protein sequence, mRNA sequence can
 . be directly used as an input in VaxPress.

```bash
# Example usage of VaxPress as an interface to LinearDesign
vaxpress -i spike.fa -o results-spike --processes 36 \
         --iterations 10 --lineardesign 1.0 \
         --conservative-start 10 --initial-mutation-rate 0.01 \
         --lineardesign-dir /path/to/LinearDesign \
```

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

Ju, Ku, and Chang (2023) Title. Journal. Volume.

# License

VaxPress is distributed under the terms of the [MIT License](LICENSE.txt).

LinearFold and LinearDesign are licensed for non-commercial use
only. If considering commercial use, be cautious about using options
such as `--lineardesign` and `--folding-engine linearfold`.
