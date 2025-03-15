# CAMP Module Template

[![Documentation Status](https://img.shields.io/readthedocs/camp_module_template)](https://camp-documentation.readthedocs.io/en/latest/) ![Version](https://img.shields.io/badge/version-0.8.2-brightgreen)

## Overview

The Cookiecutter template for all CAMP (**C**ore **A**nalysis **M**etagenomics **P**ipeline) modules. 

## Features

* Standardized Snakemake workflow with preset working directory structures and input/output formats for multi-sample metagenomics data
* Click command line interface for streamlined parameter management
* Pre-packaged Conda environment YAMLs for easy environment setup and conflict-free dependency management
* Centralized parameter and computational resource management
* Integrated Slurm (HPC cluster job submission) and command-line modes
* Included test metagenomics sequencing dataset for installation checking
* Pre-configured version bumping with a single command

> [!TIP]
> All databases used in CAMP modules will also be available for download on Zenodo (link TBD).

## Making a New Module

These instructions are only for developers that want to create an module for a **new** analysis purpose i.e.: ingests new formats of input or output data. To use or extend existing analysis modules, see TBA. 

### Part 1: Setting up the Module Barebones

1. Have [conda](https://github.com/conda-forge/miniforge>) and Cookiecutter (version 1.4.0 or higher) installed on your system. We recommend `miniforge`, which is a minimal conda installer that, by default, installs packages from open-source community-driven channels such as `conda-forge`.
```Bash
# If you don't already have conda on your system...
# wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

conda install -c conda-forge cookiecutter # or...
pip install -U cookiecutter
```

2. Use this template to generate a barebones CAMP analysis module and follow the prompts.

```Bash
cookiecutter https://github.com/MetaSUB-CAMP/CAMP_Module_Template
```

3. Set up the module environment.

```Bash
conda create -f configs/conda/module.yaml
conda activate module
```

### Part 2: Writing Module Steps (Rules)

1. Develop Snakemake rules to wrap your analysis scripts and/or external programs. There is an example (sample_rule) and three rule templates in `Snakefile` as guidelines. 
    - To write to log files, add `> {log} 2>&1` after shell commands, unless the program writes to standard output. In that case, use `2> {log}`. For commands in `run` (i.e.: built-in Python script instead of shell), see the Python example in `workflow/Snakefile`.
    - If you're using external scripts and resource files that i) cannot easily be integrated into either `utils.py` or `parameters.yaml`, and ii) are not as large as databases that would justify an externally stored download, add them to `workflow/ext/` or `workflow/ext/scripts`. An example of their application can be found in `rule external_rule`. 

2. Customize the `make_config` rule in `Snakefile` to make your final output `samples.csv` as well as return any other analysis files you might want into the `final_reports` directory.
    - If you plan to integrate multiple tools into the module that serve the same purpose but with different input or output requirements (ex. for alignment, Minimap2 for Nanopore reads vs. Bowtie2 for Illumina reads), you can toggle between these different 'streams' by setting the final files expected by `make_config` using the example function `workflow_mode`.

3. Set up a cleanup function in `workflow/utils.py` to get rid of large intermediate files (ex. SAMs, unzipped FastQs). 

### Part 3: Setting up Input/Output and Directory Structure

1. Customize the structure of `configs/samples.csv` to match your input and output data, and then `ingest_samples()` in `utils.py` to properly load them. 
    - The example here summarizes Illumina paired-end FastQs and an a set of de novo assembled contigs in a FastA. 
    - Update the description of the `samples.csv` input fields in the CLI. 

2. Fill out your module's work subdirectory structure in `utils.py`, specifically `dirs.OUT`, which is where all of the intermediate and final output files go, and `dirs.LOG`, which is where all of the logs go. Try to make as many of your work directory's tree structure as possible.

3. Add any workflow-specific Python scripts to `utils.py` so that they can be called in workflow rules. This keeps the `Snakefile` workflow clean. 
    - Note: Python functions imported from `utils.py` into `Snakefile` should be debugged on the command-line first before being added to a rule because Snakemake doesn't port standard output/error well when using `run:`.

4. If applicable, use symlinks in `utils.py` between your (original) input data as described in `samples.csv` to the temporary directory (`dirs.TMP`) so that they're easy to find and won't be destroyed. 
    - To support relative paths for input files, the symlinking example uses `abspath()`. However, this will only work if the input files are in **subdirectories** of the current directory. 

### Part 4: Setting up Module Configs and Environment Files

1. Some of the analysis scripts and/or external programs will probably consume a lot of threads and RAM. Customize the amount of memory and CPUs allocated to each rule in `configs/resources.yaml`. 

2. Some rules in the module probably use constants for `shell` or `run` parameters. Add these to `configs/parameters.yaml` for easy toggling. 

3. If applicable, update the default conda config using `conda env export > config/conda/module.yaml` with your tools and their dependencies.

4. Some of your analysis scripts and/or external programs (ex. R-based scripts) will probably have dependencies that conflict with the main environment. To handle this, create a new environment and make a new conda YAML under `configs/conda`. To use it, see the usage of `conda` option in `first_rule` for an example.

### Part 5: Write Documentation and Debug Module

1. Add your module's basic installation and running instructions to the `README.md`. Then, add complete documentation to the [CAMP documentation repo](https://github.com/MetaSUB-CAMP/camp-documentation).

2. Make the default conda environment, and after setting the appropriate input from `test_data/` in `test_data/samples.csv`, and parameters/resources in `test_data/parameters.yaml` and `test_data/resources.yaml` respectively, run the module once through to make sure everything works. 
    - If none of the test data available is appropriate, please contact us so we can coordinate the addition of new tst data. 
    - The default number of cores available to Snakemake is 1 which is enough for test data, but should probably be adjusted to 10+ for a real dataset.
    - Relative or absolute paths to the Snakefile and/or the working directory (if you're running elsewhere) are accepted!
```Bash
python /path/to/camp_module/workflow/module.py test --cores 40
```

3. Trim down the data in `test_data/` so that only the necessary and sufficient input data are present.

4. Remove any test data files that are larger than 100MB because Github repos will not allow those to be pulled to remote. 

### Part 6: Data Visualization (Optional)

The `configs/conda/` directory also contains the YAML that sets up a dataviz environment that (for now) supports Jupyter Notebooks and seaborn-based plotting. You can include a Jupyter notebook that generates preset visualizations for your module's output.

### Integrating with the CAMP

If you want your module integrated into the main CAMP module, please contact [Lauren](mailto:lam4003@med.cornell.edu) or [Braden](btt4001@med.cornell.edu)!
- Please make it clear what your module intends to do by including a summary ex. "Module A Release X.Y.Z, which does B to input C and outputs D").

## Credits

- This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter>) as a simplified version of the [project template](https://github.com/audreyr/cookiecutter-pypackage>).
- Free software: MIT
- Documentation: Coming soon!