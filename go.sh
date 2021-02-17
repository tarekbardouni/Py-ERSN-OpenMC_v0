#!/bin/bash
# This script acivate openmc environment, export cross sections data path and lunch the GUI

conda activate openmc-py3.7
export OPENMC_CROSS_SECTIONS=/home/username/OpenMC-2020/data/B7.1_hdf5/cross_sections.xml
python3 main.py
