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
  Provides data-loading and preprocessing utilities for the landscape instances used in the computational experiments, including patch areas, costs, adjacency relationships, spatial coordinates, and other instance-specific data.

- `data/`  
  Input data for the computational experiments.

- `output/`  
  Additional preprocessed data used by some instances.

## Requirements

The code is written in Python and uses Gurobi for mathematical optimization.

Main Python packages include:

- `gurobipy`
- `numpy`
- `scipy`
- `matplotlib`
- `shapely`
- `pqdict`
- `openpyxl`
- `xlwt`

A valid Gurobi license is required.

## Running the Code

The three optimization approaches can be run independently:

```bash
python R_MIP.py
python Base_MIP.py
python Dinkelbach.py
