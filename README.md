# Reock Compactness Reserve Design

This repository contains the source code and data used for the paper:

**“An Optimization Model and Exact Algorithm for the Design of Compact Nature Reserves”**  
Amirreza Saffarian, Shreyas Ravishankar, and Jorge A. Sefair

The study develops optimization approaches for conservation reserve design using the Reock compactness measure.

## Repository Contents

- `R_MIP.py`  
  Implementation of the proposed R-MIP approach.

- `Base_MIP.py`  
  Implementation of the Base-MIP formulation used for comparison.

- `Dinkelbach.py`  
  Implementation of the Dinkelbach-based solution approach.

- `load_forest_data.py`  
  Provides data-loading and preprocessing utilities for the landscape instances used in the computational experiments, including patch areas, costs, adjacency relationships, and spatial coordinates.

- `load_forest_data1.py`  
  Additional data-loading utilities used by the optimization implementations.

- `data/`  
  Contains the input data required for the computational experiments.

- `output/`  
  Contains additional preprocessed data required by some instances, including the El Dorado instance.

## Requirements

The code is written in Python and uses Gurobi for mathematical optimization.

Main Python packages include:

- `gurobipy`
- `numpy`
- `scipy`
- `pandas`
- `matplotlib`
- `shapely`
- `pqdict`
- `openpyxl`
- `xlrd`
- `xlwt`

A valid Gurobi license is required.

## Data

All input files should be stored in the `data/` directory.

The data-loading scripts read landscape information such as patch areas, costs, adjacency relationships, spatial coordinates, age, volume, and profit data.

The file `point_datasets.xlsx` should also be placed in the `data/` directory when using `load_forest_data1.py`, since this loader reads spatial-coordinate data for some landscape instances from this file.

Additional preprocessed files required by specific instances should be stored in the `output/` directory.

## Running the Code

The three optimization approaches can be run independently from the repository root:

```bash
python R_MIP.py
python Base_MIP.py
python Dinkelbach.py
