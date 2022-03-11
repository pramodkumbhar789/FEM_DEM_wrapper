# Developed by  
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.


################################ Purpose #########################################
# Automation of the generating the dat files for the visualisation.
##################################################################################


# Get all respective files

import os
import itertools
import numpy as np

file_list = os.listdir(os.getcwd())
path = os.getcwd()
count = 0

for i in file_list:
	if 'Node' in i:
		count += 1

tec_file = open('Tecplot_data.dat', 'w+')
tec_file.write("TITLE     = ABAQUS")
tec_file.write('\nVARIABLES = "X","Y","Z","Displacementx", "Displacementy", "Concentration", "S11", "S22", "S12", "S33", "SH", "E11","E22","E12"')

for p in range(count):

	with open('Node'+str(p)+'.txt') as file:
		node_data = file.read()
		
	node_data = node_data.split('\n')

	nodex = []
	nodey = []

	for i in range(len(node_data)-1):
		nodex.append(node_data[i].split(',')[1].strip())
		nodey.append(node_data[i].split(',')[2].strip())

	with open('Element'+str(p)+'.txt') as file:
		element_data = file.read()
		
	element_data = element_data.split('\n')

	element_all = []

	for i in range(len(element_data)-1):
		element = []
		element.append(element_data[i].split(',')[1].strip())
		element.append(element_data[i].split(',')[2].strip())
		element.append(element_data[i].split(',')[3].strip())
		element_all.append(element)

	# In 'element_all_flat', only vertex nodes are present	
	element_all_flat = list(itertools.chain.from_iterable(element_all))
	element_all_flat.sort()
	element_all_flat = list(map(int, element_all_flat))
	element_all_flat = np.unique(element_all_flat) 

	with open('disp'+str(p)+'.txt') as file:
		disp_data = file.read()
		
	disp_data = disp_data.split('\n')

	dispx = []
	dispy = []

	for i in range(len(disp_data)-1):
		disp_data_split = filter(None, disp_data[i][1:][:-1].split(' '))
		dispx.append(disp_data_split[0])
		dispy.append(disp_data_split[1])
		
	with open('Temp'+str(p)+'.txt') as file:
		temp_data = file.read()
		
	temp_data = temp_data.split('\n')

	temp_all = []

	for i in range(len(temp_data)-1):
		temp_all.append(temp_data[i])
		
	with open('stress'+str(p)+'.txt') as file:
		stress_data = file.read()
		
	stress_data = stress_data.split('\n')

	stress_all = []

	for i in range(len(stress_data)-1):
		stress_all.append(filter(None, stress_data[i][1:-2].split(' ')))
		
	with open('strain'+str(p)+'.txt') as file:
		strain_data = file.read()
		
	strain_data = strain_data.split('\n')

	strain_all = []

	for i in range(len(strain_data)-1):
		strain_all.append(filter(None, strain_data[i][1:-2].split(' ')))


	tec_file.write('\nZONE T="'+str(p)+'"'+'\t'+'SOLUTIONTIME='+str(path.split('/')[-3].split('_')[-1])) 
	tec_file.write('\nNodes='+str(len(element_all_flat))+', Elements='+str(len(element_all))+', ZONETYPE=FETRIANGLE')
	tec_file.write('\nDATAPACKING=POINT')

	for i in range(len(element_all_flat)): # Writing only the vertex nodes
		tec_file.write('\n' + nodex[i] + ' ' + nodey[i] + ' ' + str(0) + ' ' + dispx[i] + ' ' + dispy[i] + ' ' + temp_all[i] + ' ' + stress_all[i][0] + ' ' + stress_all[i][1] + ' ' + stress_all[i][2] + ' ' + stress_all[i][3] +' ' + stress_all[i][4] + ' '+ strain_all[i][0] + ' ' + strain_all[i][1] + ' ' + strain_all[i][2])

	tec_file.write('\n')

	for i in range(len(element_all)):
		tec_file.write('\n'+ element_all[i][2] + ' ' + element_all[i][1] + ' ' + element_all[i][0])
	
tec_file.close()
