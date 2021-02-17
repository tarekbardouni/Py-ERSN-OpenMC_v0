How to use the GUI to install openmc and prerequisistes under miniconda3
Prof. Tarek El Bardouni, University Abdelmalek Essaadi, Tetouan, Morocco

A/  Install first gcc g++ and cmake if doesn't exist

B/ 	Before runing the GUI: install python3-pyqt5
	
	sudo apt install python3-pyqt5

	or pyqt5-dev and pyqt5-dev-tools

C/	run the application
run : python3 main.py
	1. install miniconda3 and update its packages
	2. close and reopen the terminal
	3. make sur the conda is activated
	4. as pyqt5 is not yet installed under conda lunch the GUI by runing :
		/usr/bin/python3 main.py 
	5. install prerequisites
	6. install openmc
	7. download neutron data

C/	runing openmc under the GUI
script to lunch the gui to run openmc : 

conda activate openmc-py3.7
export OPENMC_CROSS_SECTIONS=/home/tarek/Py-OpenMC-2020/data/endfb71_hdf5/cross_sections.xml
# export OPENMC_CROSS_SECTIONS=/home/tarek/Py-OpenMC-2020/data/nndc_hdf5/cross_sections.xml
python3 gui.py
