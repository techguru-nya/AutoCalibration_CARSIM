# ESP Auto-Tuning using Simulation
This project implements an auto-tuning system for the Electronic Stability Program (ESP) using simulations. The project involves running MATLAB and CARSIM simulations, modifying parameters with PMSe, and applying Optuna for parameter tuning.

## Features
- Simulates ESP performance using MATLAB and CARSIM.
- Modifies parameters using PMSe (Parameter Management System for Evaluation).
- Uses Optuna for automated parameter tuning to optimize ESP performance.

## Requirements
- MATLAB
- CARSIM
- PMSe
- Python

## How to Use
1. Ensure that MATLAB and CARSIM are installed and properly configured.
2. Open JupyterLab.
5. Open `main.ipynb` and set the necessary paths for your simulation and parameter files.
6. Run all cells in the notebook to execute the simulation and parameter tuning.

## Workflow
1. **Simulation Execution**:  
   Run simulations using MATLAB and CARSIM to assess ESP performance under different conditions.
2. **Parameter Modification**:  
   Use PMSe to adjust ESP parameters during the simulation to see how different settings affect performance.
3. **Parameter Tuning**:  
   Use Optuna to automatically tune the ESP parameters for optimal performance.
4. **Analysis**:  
   After tuning, analyze the performance improvements and determine the best parameters for ESP.

## Results
The tool outputs:
- Optimized ESP parameters based on simulation results.
- Performance metrics and visualizations showing the improvements achieved by parameter tuning.
