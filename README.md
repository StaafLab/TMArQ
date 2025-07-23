# TMArQ

## About

TMArQ, Tissue microarray MArker Quantification, is a pipeline for automated quantification of antibody staining in TMA cores.
It can automatically process TMA core images of several markers taken from several TMA blocks. The user only needs to provide the names of the TMA block and marker directories.

TMArQ works as follows:

1) Detection of region of interest (ROI) using Hough circle detection. If no circle is detected, the image can be excluded from downstream analysis.
2) Colour deconvolution to separate out the DAB staining from the hematoxylin staining.
3) Thresholding signal in the DAB layer to determine DAB absence/presence on the level of individual pixels.
4) Cell nuclei segmentation using starDist.
5) Combining starDist detected cells with the DAB staining layer to count IHC-stained cells in the core. Of note: TMArQ creates summary output files per core as default, but it can also output files containing a list of positive cells and their coordinates per core by changing the save_per_cell flag in the config file to true.

 <img src='./tmarq_git.png' alt='TMArQ pipeline' width=60%>

For more information, see our 2024 publication ["Tumour immune characterisation of primary triple-negative breast cancer using automated image quantification of immunohistochemistry-stained immune cells"](https://www.nature.com/articles/s41598-024-72306-1) in Scientific Reports.

## Installation

### Using a conda environment

To use TMArQ you will first need to install conda. Follow the information available on https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html

With conda installed, clone this repository and create a new conda environment with the required packages listed in the included file. Alternatively, TMArQ can be run within a Singularity container. Scroll down for more information.

```
git clone https://github.com/StaafLab/TMArQ
cd TMArQ
conda env create -f env/tmarq.yml
```

## Getting started

TMArQ comes with an example data set. To run this example, activate the conda environment and run the workflow with Snakemake. 

```
conda activate tmarq
snakemake -jall
```

## Specifying your own files

TMArQ expects individual core images under:
- data
  - blockname 
    - markername
 
 1. Specify your block and marker names in the config file, which is located in the directory config (see config_example.yml for an example).

 2. Specify the name of your config file in the Snakemake file (Snakefile). 

 TMArQ expects core images that are a bit over 3000x3000 pixels, as this is the standard dearrayed output from pathXL, a platform enabling digital pathology. If you want to update the image dimensions, you can easily do this in the tmaConfig.yml file under config.

 3. Then run your code as in the example above. You can specify the number of cpu cores you want to use for the run using the -j flag. In the example we use all available cores. 

```
conda activate tmarq
snakemake -jall
```

 The run will create a results/ directory with the following directories: 
 - 01_coordinates: core coordinates per image
 - 02_segment/meta: information such as which images should be excluded from analysis
 - 02_segment/per_core: total cell counts per core
 - 02_segment/pos_cells: coordinates of positive cells (only created when the save_per_cell flag is set to true)


## Using a Singularity container

To use TMArQ with a container, Singularity must be installed. Follow the information available on https://docs.sylabs.io/guides/3.8/admin-guide/installation.html or, alternatively, create (and activate) a conda environment that contains Singularity. After cloning this repo, go into the TMArQ/ directory, build the container using the provided .def file (only needs to be performed once to create the .sif file), and run TMArQ as shown below for as many blocks and markers as needed.

```
git clone https://github.com/StaafLab/TMArQ
cd TMArQ
singularity build --fakeroot tmarq.sif singularity/tmarq_singularity.def
# to run the example data
singularity exec --bind /path/to/TMArQ:/workspace tmarq.sif \
    bash -c "source /opt/miniconda3/etc/profile.d/conda.sh; conda activate tmarq; snakemake -jall"
# to run with your own data
singularity exec --bind /path/to/TMArQ:/workspace tmarq.sif bash singularity/run_tmarq.sh
```

In the code above, we are first binding our current TMArQ directory (make sure you have the correct path as it is in your computer) to the workspace used by the container. This is needed so that the container can find the necessary files. Then, inside the container tmarq.sif, we execute TMArQ using a simplified bash command or by using a slightly longer bash script called run_tmarq.sh. This file makes sure conda can be used in the container, activates the tmarq conda environment, and runs TMArQ using Snakemake and the information you have provided in its config file. If your images are not inside TMArQ/data/ but somewhere else in your computer and you do not wish to copy the files, you can use the two lines of code commented out in the bash script (as long as there is not already a data/ directory in TMArQ - that is, it would be necessary to delete the included data/ directory). The code creates a symbolic link between where your data are stored and a data/ directory within TMArQ/, and unlinks the original data from the TMArQ/data/ directory after finishing the analysis.

## License

Copyright (C) 2023 Suze Roostee

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
