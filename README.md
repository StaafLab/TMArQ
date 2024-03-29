# Tissue mircoarray MArker Quantification (TMArQ)

## About

This is a pipeline for quantification of antibody staining in TMA cores.

## Installation

To use TMArQ you will first need to install conda, see https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html

To run the code in this repository, the easiest is to clone it and then install the requirements

```
git clone https://github.com/StaafLab/TMArQ
cd TMArQ
conda env create -f tmarq.yml
```

## Usage

To run this pipeline, activate the conda environment and run snakemake

```
conda activate tmarq
snakemake -jall
```

## License

Copyright (C) 2023 Suze Roostee

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.


