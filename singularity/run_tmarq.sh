#!/bin/bash

## make sure conda can be used in the container
source /opt/miniconda3/etc/profile.d/conda.sh
## link another directory to TMArQ data/ if needed
# ln -s /path/to/data/folder/in/computer ./data
## active the conda environment
conda activate tmarq
## run TMArQ with Snakemake
snakemake -jall
## unlink the data
# unlink data
