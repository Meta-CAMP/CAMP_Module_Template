{% set is_open_source = cookiecutter.open_source_license != 'Not open source' -%}

# CAMP {{ cookiecutter.module_name }}

{% if is_open_source %}
[![Documentation Status](https://img.shields.io/readthedocs/camp_{{ cookiecutter.module_slug }})](https://camp-documentation.readthedocs.io/en/latest/{{ cookiecutter.module_slug }}.html) 
{%- endif %}

![Version](https://img.shields.io/badge/version-{{ cookiecutter.version }}-brightgreen)

## Overview

This module is designed to function as both a standalone MAG {{ cookiecutter.module_name }} pipeline as well as a component of the larger CAMP metagenomics analysis pipeline. As such, it is both self-contained (ex. instructions included for the setup of a versioned environment, etc.), and seamlessly compatible with other CAMP modules (ex. ingests and spawns standardized input/output config files, etc.). 

{{ cookiecutter.module_short_description }}
<!--- 
Add longer description of your workflow's algorithmic contents 
--->

## Installation

1. Clone repo from [Github](https://github.com/MetaSUB-CAMP/camp_{{ cookiecutter.module_slug }}).
```Bash
git clone https://github.com/MetaSUB-CAMP/camp_{{ cookiecutter.module_slug }}
```

2. Set up the conda environment (contains Snakemake, Click, and other essentials) using `configs/conda/{{ cookiecutter.module_slug }}.yaml`. 

If you don't already have `conda` handy, we recommend installing `miniforge`, which is a minimal conda installer that, by default, installs packages from open-source community-driven channels such as `conda-forge`.
```Bash
# If you don't already have conda on your system...
# wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh

# Create and activate conda environment 
cd camp_{{ cookiecutter.module_slug }}
conda env create -f configs/conda/{{ cookiecutter.module_slug }}.yaml
conda activate {{ cookiecutter.module_slug }}
```

3. Update the relevant parameters (if applicable- for example, location of external non-conda tools) in `test_data/parameters.yaml`.

4. Make sure the installed pipeline works correctly. 
<!--- 
Add runtime information of the module on the test dataset here. For example: With X threads and a maximum of Y GB allocated, the dataset should finish in approximately Z minutes.
--->
```Bash
# Run tests on the included sample dataset
python /path/to/camp_{{ cookiecutter.module_slug }}/workflow/{{ cookiecutter.module_slug }}.py test
```

## Using the Module

**Input**: `/path/to/samples.csv` provided by the user.

**Output**: 1) An output config file summarizing 2) the module's outputs. 

- `/path/to/work/dir/{{ cookiecutter.module_slug }}/final_reports/samples.csv` for ingestion by the next module (ex. quality-checking)
<!--- 
Add description of your workflow's output files 
--->

### Module Structure
```
└── workflow
    ├── Snakefile
    ├── {{ cookiecutter.module_slug }}.py
    ├── utils.py
    ├── __init__.py
    └── ext/
        └── scripts/
```
- `workflow/{{ cookiecutter.module_slug }}.py`: Click-based CLI that wraps the `snakemake` and other commands for clean management of parameters, resources, and environment variables.
- `workflow/Snakefile`: The `snakemake` pipeline. 
- `workflow/utils.py`: Sample ingestion and work directory setup functions, and other utility functions used in the pipeline and the CLI.
- `ext/`: External programs, scripts, and small auxiliary files that are not conda-compatible but used in the workflow.

### Running the Workflow

1. Make your own `samples.csv` based on the template in `configs/samples.csv`. Sample test data can be found in `test_data/`. 
    - For example, `ingest_samples` in `workflow/utils.py` expects Illumina reads in FastQ (may be gzipped) form and de novo assembled contigs in FastA form
    - `samples.csv` requires either absolute paths or paths relative to the directory that the module is being run in.

2. Update the relevant parameters in `configs/parameters.yaml`.

3. Update the computational resources available to the pipeline in `configs/resources.yaml`. 

#### Command Line Deployment

To run CAMP on the command line, use the following, where `/path/to/work/dir` is replaced with the absolute path of your chosen working directory, and `/path/to/samples.csv` is replaced with your copy of `samples.csv`. 
    - The default number of cores available to Snakemake is 1 which is enough for test data, but should probably be adjusted to 10+ for a real dataset.
    - Relative or absolute paths to the Snakefile and/or the working directory (if you're running elsewhere) are accepted!
    - The parameters and resource config YAMLs can also be customized.
```Bash
python /path/to/camp_{{ cookiecutter.module_slug }}/workflow/{{ cookiecutter.module_slug }}.py \
    (-c number_of_cores_allocated) \
    (-p /path/to/parameters.yaml) \
    (-r /path/to/resources.yaml) \
    -d /path/to/work/dir \
    -s /path/to/samples.csv
```

#### Slurm Cluster Deployment

To run CAMP on a job submission cluster (for now, only Slurm is supported), use the following.
    - `--slurm` is an optional flag that submits all rules in the Snakemake pipeline as `sbatch` jobs. 
    - In Slurm mode, the `-c` flag refers to the maximum number of `sbatch` jobs submitted in parallel, **not** the pool of cores available to run the jobs. Each job will request the number of cores specified by threads in `configs/resources/slurm.yaml`.
```Bash
sbatch -J jobname -o jobname.log << "EOF"
#!/bin/bash
python /path/to/camp_{{ cookiecutter.module_slug }}/workflow/{{ cookiecutter.module_slug }}.py --slurm \
    (-c max_number_of_parallel_jobs_submitted) \
    (-p /path/to/parameters.yaml) \
    (-r /path/to/resources.yaml) \
    -d /path/to/work/dir \
    -s /path/to/samples.csv
EOF
```

#### Finishing Up

1. To quality-check the processed FastQs, download and compare the collated MultiQC reports, which can be found at `/path/to/work/dir/short_read_qc/final_reports/*_multiqc_report/html`. Multiple rounds of preprocessing may be needed to fully get rid of low-quality bases, adapters, and duplicated sequences. 
    - For example, the dataset I worked with required an additional round of `fastp` to trim 10 low-quality bases from the 5' and 4 low-quality bases from the 3' end respectively. 
    - I recommend creating a new directory, which I've called `/path/to/work/dir/short_read_qc/5_retrimming` and placing reprocessed reads inside them. 
    - Afterwards, I reran FastQC and MultiQC and collated summary statistics (ex. numbers of reads, etc.) from the reprocessed datasets manually. I also updated the location of the reprocessed reads in `/path/to/work/dir/short_read_qc/final_reports/samples.csv` to `/path/to/work/dir/short_read_qc/5_retrimming`.

2. To plot grouped bar graph(s) of the number of reads and bases remaining after each quality control step in each sample, set up the dataviz environment and follow the instructions in the Jupyter notebook:
```Bash
conda env create -f configs/conda/dataviz.yaml
conda activate dataviz
jupyter notebook &
```

3. After checking over `final_reports/` and making sure you have everything you need, you can delete all intermediate files to save space. 
```Bash
python3 /path/to/camp_{{ cookiecutter.module_slug }}/workflow/{{ cookiecutter.module_slug }}.py cleanup \
    -d /path/to/work/dir \
    -s /path/to/samples.csv
```

4. If for some reason the module keeps failing, CAMP can print a script containing all of the remaining commands that can be run manually. 
```Bash
python3 /path/to/camp_{{ cookiecutter.module_slug }}/workflow/{{ cookiecutter.module_slug }}.py --dry_run \
    -d /path/to/work/dir \
    -s /path/to/samples.csv
```

## Credits

- This package was created with [Cookiecutter](https://github.com/cookiecutter/cookiecutter) as a simplified version of the [project template](https://github.com/audreyr/cookiecutter-pypackage).
{% if is_open_source %} 
- Free software: {{ cookiecutter.open_source_license }} License
- Documentation: https://camp-documentation.readthedocs.io/en/latest/{{ cookiecutter.module_slug }}.html
{% endif %}


