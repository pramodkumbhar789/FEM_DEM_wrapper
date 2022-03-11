# Developed by 
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.

################################ Purpose #########################################
# Automated Abaqus inp file modification
##################################################################################

from __future__ import division
def modinp(info_file):
	
	# --------------------------------------------------------------------------- #
	
	# Uncomment the next few lines only for debugging purposes 
	
	#global group_temp_assigned_reordered, group_temp_assigned_flattened, repeated_id, particle2x_flatten
	
	#global data_node_previous, data_center_positions_previous, group_data, assigned_conc_all, grouped_particle_list_current, xmod, ymod, xp, yp, xpn, ypn, x, y, x1, y1
	
	#global particle1x_all,particle1y_all,particle2x_all,particle2y_all, temp_data, grouped_node_list_current, xpr, ypr, assigned_conc_values_averaged, grouped_node_list_current_reordered

	#global grouped_particle_list_previous, data_center_positions_previous, required_groups, database_data, group_info, xpn_string, x_info
	
	# --------------------------------------------------------------------------- #
	
	# Import modules

	import os
	import Tkinter as tk
	from tkFileDialog import askopenfilename as ask
	import numpy as np
	from time import strftime
	
	
	# --------------------------------------------------------------------------- #
	#global username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,timestep 
	
	# Set UVARM switch and read domain information
	
	with open(info_file) as file:
		for line in file:
			if 'UVARM = ' in line:
				UVARM = np.int(line.split('=')[1].strip()); break
			else:
				UVARM = 0
	with open(info_file) as file:
		for line in file:
			if 'Domain info: XMax' in line:
				x_domain_max = np.float64(line.split('=')[1].split('\n')[0].strip())
			elif 'Domain info: YMax' in line:
				y_domain_max = np.float64(line.split('=')[1].split('\n')[0].strip())
			elif 'Domain info: XMin' in line:
				x_domain_min = np.float64(line.split('=')[1].split('\n')[0].strip())
			elif 'Domain info: YMin' in line:
				y_domain_min = np.float64(line.split('=')[1].split('\n')[0].strip())

	# --------------------------------------------------------------------------- #
	
	''' 
	
	This function is responsible for the modification of the inp files.
		
	REQUIREMENTS:
	
	-> ABAQUS inp files (non-modified data).
		
	USAGE:
	
	-> Can be executed through wrapper_main.py
	-> Can be run standalone. In this case, please add modinp() at the end 
	of the script.
		
	'''
	
	# --------------------------------------------------------------------------- #
	
	# Set timestep for the inp modification
	




	timestep_switch = 2
	
	# --------------------------------------------------------------------------- #

	# Define functions
	
	# The following function is useful for comparing the circle intersections. 
	# This is used twice in the script. 
	# Detailed info is given later.

	def compare(x1, y1, x2, y2, r1, r2):
		distsq = np.sqrt((x1-x2)**2 + (y1-y2)**2)
		radsum = r1+r2
		
		if distsq < radsum:
			return -1
			
	# This function is responsible for converting data in cartesian coordinates 
	# to polar coordinates.
			
	def cart2pol(x, y):
		rho = np.sqrt(x**2 + y**2)
		phi = np.arctan2(y, x)
		return(rho, phi)
		
	# This function is responsible for converting data in polar coordinates 
	# to cartesian coordinates.

	def pol2cart(rho, phi):
		x = rho * np.cos(phi)
		y = rho * np.sin(phi)
		return(x, y)
		
	# Define function to update info file
	
	def info_update(update_line):
		Info_file = open(info_file, 'a')
		Info_file.write(strftime('[%H:%M:%S]'+'\t\t\t'+update_line+'\n'))
		Info_file.close()

	# --------------------------------------------------------------------------- #

	# Initialize

	root = tk.Tk()
	root.withdraw()
	current_dir = os.getcwd()
	os.system('clear')
	count = 0
	
	# --------------------------------------------------------------------------- #

	# Initialize data lists

	heading_list = []
	preprint_list = []
	node_list = []
	element_list = []
	part_list = []
	assembly_list = []
	material_prop = []
	initial_conditions = []
	step = []
	
	# --------------------------------------------------------------------------- #

	# Read inp file 

	inp_file = 'Job_2.inp'

	with open(inp_file) as file:
		data = file.read()
		
	data = data.split('\n')
	
	info_update('Read inp file: '+inp_file)
	
	# --------------------------------------------------------------------------- #

	# Break down contents of the inp file and store it in lists initiated previously

	fn = open('Node2.txt','w+')
	fe = open('Element2.txt','w+')
	fuvarm = open('Element_uvarm2.txt','w+')
	fuvarm.write('*Element, type=CPS6MT\n')

	while True:
		
		if '*Heading' in data[count]:
			heading_list.append(data[count])
			count += 1
			
			while True:
				if '**' in data[count]:
					heading_list.append(data[count])
					count += 1
				else:
					break
		
		elif '*Preprint' in data[count]:
			preprint_list.append(data[count])
			count += 1
			
			while True:
				if '**' in data[count]:
					preprint_list.append(data[count])
					count += 1
				else:
					break
		
		elif '*Part' in data[count]:
			while True:
				if '*Node' in data[count]:
					node_list.append(data[count])
					count += 1
					while True:
						if '*' in data[count]:
							break
						else:
							fn.write(data[count])
							fn.write('\n')
							node_list.append(data[count])
							count += 1
				elif '*Element' in data[count]:
					element_list.append(data[count])
					count += 1
					count_uvarm = 1
					while True:
						if '*' in data[count]:
							break
						else:
							fe.write(data[count])
							fuvarm.write(str(100000+count_uvarm)+','+','.join(data[count].split(',')[1:]))
							fuvarm.write('\n')
							fe.write('\n')
							element_list.append(data[count])
							count += 1
							count_uvarm += 1
				elif '*End Part' in data[count]:
					part_list.append(data[count])
					count += 1
					break
				else:
					part_list.append(data[count])
					count += 1
					
		elif '**' in data[count]:
			while True:
				if '*Assembly' in data[count] or '*Step' in data[count]:
					break
				else:
					count += 1
		
		elif '*Assembly' in data[count]:
			while True:
				if '*End Assembly' in data[count]:
					assembly_list.append(data[count])
					count += 1
					break
				else:
					assembly_list.append(data[count])
					count += 1
		
		elif '*Material' in data[count]:
			while True:
				if '*Initial Conditions' in data[count]:
					break
				else:
					material_prop.append(data[count])
					count += 1
		
		elif '*Initial Conditions' in data[count]:
			while True:
				if '**' in data[count]:
					break
				else:
					initial_conditions.append(data[count])
					count += 1
					
		elif '*Step' in data[count]:
			while True:
				if '*End Step' in data[count]:
					step.append(data[count])
					count += 1
					break
				#elif '**' in data[count]:
					#print data[count]
					#count += 1
				else:
					step.append(data[count])
					count += 1
		else:
			break

	fn.close()
	fe.close()
	fuvarm.close()
	
	info_update('Breakdown of inp file complete...')
	
	# --------------------------------------------------------------------------- #
			
	# Create new inp file for writing the modified data

	fnew = open('Job__2s.inp','w+')
	
	info_update('New inp file: '+inp_file[:5]+'s.inp')
	
	# --------------------------------------------------------------------------- #

	# Write heading data to new inp file

	for i in heading_list:
		fnew.write(i)
		fnew.write('\n')
		
	info_update('Heading data written...')
	
	# --------------------------------------------------------------------------- #

	# Write preprint data to new inp file

	for i in preprint_list:
		fnew.write(i)
		fnew.write('\n')
		
	#info_update('Preprint data written...')
	
	# --------------------------------------------------------------------------- #
		
	# Write part data to new inp file and point file to node data

	for count, i in enumerate(node_list):
		if '*Node' in i and not 'input' in i:
			node_list[count] = node_list[count] + ', input=Node2.txt'
			fnew.write(node_list[count])
			fnew.write('\n')
			break
		else:
			fnew.write('*Node,NSET=all,input=Node2.txt')
			fnew.write('\n')
			break
	
	info_update('Node data written to file: Node' + inp_file[4:5] +'.txt')
	
	# --------------------------------------------------------------------------- #
	
	# Write UEL information to new inp file

	fnew.write('*User element, nodes=6, type=U1, properties=4,variables=7, coordinates=2, UNSYMM\n')		# Properties for calculation set as 5, variables to be output set as 7
	fnew.write('1,2,11\n')																					# 1 corresponds to x-dir, 2 corresponds to y-dir and 11 corresponds to temperature. DOF.

	for count, i in enumerate(element_list):
		if '*element' in i and not 'input' in i:
			element_list[count] = element_list[count] + ', input=element2.txt'
			fnew.write(element_list[count])
			fnew.write('\n')
			break
		else:
			fnew.write('*Element, type=U1, Elset=ALL,input=Element2.txt')
			fnew.write('\n')
			break
	
	info_update('Element data written to file: Element' + inp_file[4:5] +'.txt')
	
	# --------------------------------------------------------------------------- #
			
	# Set UEL property in new inp file

	fnew.write('*UEL Property, Elset=all\n')
	fnew.write('19.25d9,0.3,4.17d-6,2.64d4,300.0\n')    # Physical property
	
	info_update('UEL properties written...')
	
	# --------------------------------------------------------------------------- #
	
	# Write end node and element properties in new inp file

	fnew.write('*Nset, nset=sec_assign, generate\n')			# For node data
	fnew.write(' 1,  ' + str(len(node_list)-1) + ',  1\n')			# Start node, end node, increment
	info_update('Node Nset written...')  
	fnew.write('*Elset, elset=sec_assign, generate\n')						# For element data
	fnew.write(' 1,  ' + str(len(element_list)-1) + ',  1\n')				# start element, end element, increment
	info_update('Element Elset written...')
	
	if UVARM == 1:
		fnew.write('*include, input=Element_uvarm2.txt')
		fnew.write('\n*Elset, elset=dummy,generate\n')
		fnew.write('100001,'+str(100000+count_uvarm-1)+',1\n')		# Offset is set to 1,00,000 for UVARM Visualization
		info_update('UVARM Elset written...')
	
	# --------------------------------------------------------------------------- #
			
	# Create Nset for Mechanical BC

	set_val = 'MBC'

	fnew.write('*Nset, nset='+set_val)
	
	# --------------------------------------------------------------------------- #

	# Read group data of the current timestep.

	with open('../Group2.txt') as file:
		group_data = file.read()
	
	group_data = group_data.split('\n')
		
	xpn = []															# x data at centre
	ypn = []															# y data at centre
	xprn = []															# x data at circumference
	yprn = []															# y data at circumference
	radn = []															# radius of the particle
	for i in range(len(group_data)-1):
		temp = filter(None, group_data[i].split(' '))
		xpn.append(np.float64(temp[0]))
		ypn.append(np.float64(temp[1]))
		xprn.append(np.float64(temp[2]))
		yprn.append(np.float64(temp[3]))
		radn.append(np.float64(temp[2]) - np.float64(temp[0]))
	
	# --------------------------------------------------------------------------- #

	# Read node data at current timestep 

	with open('Node2.txt') as file:
		data = file.read()
		
	data = data.split('\n')

	x = []
	y = []

	for i in range(len(data)-1):
		x.append(np.float64(data[i].split(',')[1]))
		y.append(np.float64(data[i].split(',')[2]))
		
	xmean = np.average(x)												# Get mean of x
	ymean = np.average(y)												# Get mean of y
	
	center_nodes = []

	# Switch controls whether MBC data is written for particles or groups
	# For particles, the MBC points are obtained at every particle center
	# For groups, the MBC points are obtained at the group center
	# If the program fails to find the MBC points at the group center, a random node is chosen. 

	particle_data = 'yes'
	
	if particle_data == 'yes':
		for i in range(len(xpn)):
			center_temp = []
			increment = 0
			while True:
				if len(center_temp) < 2:
					for k in range(len(x)):
						if compare(xpn[i], ypn[i], x[k], y[k], np.average((radn[i])/10)+increment, 0) == -1:
							if not k+1 in center_temp and len(center_temp) <=2:
								center_temp.append(k+1)
					increment += radn[i]/20
				elif increment > 0 and len(center_temp) >= 2:
					center_nodes.append(str(center_temp[0]))
					center_nodes.append(str(center_temp[1]))
					break
			info_update('MBC fixed for particle '+str(i+1))
	
	else:
		#for i in range(len(x)):
			#if compare(xmean, ymean, x[i], y[i], np.average(radn)/4, 0) == -1:
				#center_nodes.append(i+1)
		#info_update('MBC fixed for Group '+inp_file[4:5])
				
	#if len(center_nodes) < 1:
		max_val = [i for i in range(len(radn)) if radn[i]==max(radn)]
		center_temp = []
		increment = 0
		while True:
			if len(center_temp) < 2:
				for k in range(len(x)):
					if compare(xpn[max_val[0]], ypn[max_val[0]], x[k], y[k], np.average((radn[max_val[0]])/10)+increment, 0) == -1:
						if not k+1 in center_temp and len(center_temp) <=2:
							center_temp.append(k+1)
				increment += radn[max_val[0]]/20
			elif increment > 0 and len(center_temp) >= 2:
				center_nodes.append(str(center_temp[0]))
				center_nodes.append(str(center_temp[1]))
				break
		info_update('Center nodes for MBC fixed for largest particle')

	# Write the MBC data to the new inp file 
	fnew.write('\n')
	for i in range(len(center_nodes)):
		if i == len(center_nodes)-1:
			fnew.write(str(center_nodes[i])) 
		elif i > 0 and i % 15 == 0:
			fnew.write('\n')
			fnew.write(str(center_nodes[i])+',') 
		else:
			fnew.write(str(center_nodes[i])+',') 
			
	info_update('MBC data written...')

	fnew.write('\n')
	
	# --------------------------------------------------------------------------- #
	
	# Obtain Boundary nodes
	from boundary import boundary_nodes
	# Below the file read will be Job_10.inp
	bnodes = boundary_nodes(10)  
	#for i in range(len(xpn)):
	#	for j in range(len(x)):
	#		if compare(xpn[i], ypn[i], x[j], y[j], radn[i]*0.99, 0) == -1:
	#			bnodes.append(j)
				
	bnodes_all = [i for i in bnodes]
	
	# --------------------------------------------------------------------------- #

	# Next BC 

	left_concentration_bc = []

	#for i in range(len(x)):
		#if x[i] >= x_domain_min and x[i] <= (x_domain_min + ((x_domain_max - x_domain_min))/100):
			#left_concentration_bc.append(i+1)
	
	for i in range(len(bnodes_all)):
		left_concentration_bc.append(bnodes_all[i])
			
	if left_concentration_bc:
			
		set_val2 = 'Conc_disp_BC'

		fnew.write('*Nset, nset='+set_val2)
		
		fnew.write('\n')
				
		for i in range(len(left_concentration_bc)):
				if i == len(left_concentration_bc) - 1:
					fnew.write(str(left_concentration_bc[i])+'\n')
				elif i > 0 and i % 15 == 0:
					fnew.write('\n')
					fnew.write(str(left_concentration_bc[i])+',')
				else:
					fnew.write(str(left_concentration_bc[i])+',')
					
		#info_update('Concentration BC applied at 10% of the Left boundary...')
	
	info_update('Concentration BC written...')

	# --------------------------------------------------------------------------- #

	# Write material data
		
	fnew.write('*Material, name=Material-1\n\
*Conductivity\n\
1.,\n\
*Density\n\
1.,\n\
*Elastic\n\
1., 0.3\n\
*Specific Heat\n\
1., 			\n')

	if UVARM == 1:
		fnew.write('*Solid section, elset=dummy, material=Material-2\n\
*Material, name=Material-2\n\
*User output variables\n\
2\n\
*Elastic\n\
1.e-36,0.0\n\
*Conductivity\n\
1.e-36,\n\
*Density\n\
1.e-36,\n\
*Specific Heat\n\
1.e-36, \n\
*Expansion\n\
1.e-36,\n')
	if timestep_switch < 2:
		fnew.write('*Amplitude, name=Amp-1, definition=SMOOTH STEP\n\
             0.0,             0.,              0.05,             1.\n') # In this line, two things should be changed.Final should be(i.e. last entry) charge-1 or discharge-0.
	else: 
		fnew.write('*include,input=Amp2.txt\n')
	info_update('Material data written...')

	# --------------------------------------------------------------------------- #
	# Write Initial conditions
	
	finit = open('Initial2.txt', 'w+')
	fnew.write('*include,input=Initial2.txt')
	finit.write('*Initial Conditions, type=TEMPERATURE\n')
	

	
	info_update('Initial conditions written to: Initial'+inp_file[4:5]+'.txt')
	
	if timestep_switch == 1:
		
		for j in range(len(node_list)-1):
			finit.write(str(j+1) + ',' + '0\n') # charge
			#finit.write(str(j+1) + ',' + '1\n')  # discharge
		finit.close()		
		info_update('Concentration set to 0 for first timestep...')
	
	else:
		famplitude = open('Amp2.txt', 'w+')
		info_update('Concentration has to be read from previous timestep...')
				
		# Read initial concentration data from previous timestep. This is required for current assigning. 
		
		with open('../../log/Particle_database'+str(timestep_switch-1)+'.txt') as file:
			database_data = file.read()
			
		database_data = database_data.split('\n')
		
		with open('../../log/Particle_database'+str(timestep_switch)+'.txt') as file:
			database_data_current = file.read()
			
		database_data_current = database_data_current.split('\n')
		
		id_info = []
		x_info = []
		x_info_current = []
		y_info = []
		group_info = []
		group_info_current = []
		
		for i in database_data[1:-1]:
			temp = filter(None, i.split(' '))
			id_info.append(temp[0])
			x_info.append(temp[1])
			y_info.append(temp[2])
			group_info.append(temp[4])
		
		info_update('Read Particle database '+str(timestep_switch-1) + 'data')
		
		for i in database_data_current[1:-1]:
			temp = filter(None, i.split(' '))
			x_info_current.append(temp[1])
			group_info_current.append(temp[4])
			
		info_update('Read Particle database '+str(timestep_switch) + 'data')
			
		# --------------------------------------------------------------------------- #
			
		# Find max group number. Required for later use.
		
		all_groups = []
		
		for i in range(len(group_info)):
			if group_info[i] in all_groups:
				pass
			else:
				all_groups.append(group_info[i])
		
		info_update('Number of groups in current timestep: '+str(len(all_groups)))
				
		# --------------------------------------------------------------------------- #
				
		# Find particles required for comparison.
			
		xpn_string = [str(i) for i in xpn]
		
		required_particles = []
		
		for i in xpn_string:
			for j, value in enumerate(x_info_current):
				if i == value:
					required_particles.append(j)
		
		info_update('Identified required particle groups for comparison from previous group...')
					
		# --------------------------------------------------------------------------- #
					
		# For the required particles, read the temperature information, node information and group information
		# and append accordingly.
		
		required_groups = [group_info[i] for i in required_particles]
		
		required_groups_numbers = [filter(None, group_info[i].split('Group'))[0] for i in required_particles]
		
		info_update('Identified required particles for comparison...')
		info_update('Current group: ' + inp_file[4:5] )
		info_update('Groups chosen for comparison: '+ str(required_groups_numbers))
		
		# --------------------------------------------------------------------------- #
		
		# Initialize lists
		
		xp = []
		yp = []
		xpr = []
		ypr = []
		rad = []
		grouped_particle_list_previous = []
		grouped_temperature_list_previous = []
		grouped_node_list_previous = []
		particle1x_all = []
		particle1y_all = []
		
		for i in range(len(required_particles)):
			
			# Access previous data Group information and obtain corresponding center data.
			
			with open('../../MDPM_'+str(timestep_switch-1)+'/' + required_groups[i] + '.txt') as file:
				data_center_positions_previous = file.read()
				
			data_center_positions_previous = data_center_positions_previous.split('\n')
			for j in range(len(data_center_positions_previous)-1):
				temp = filter(None, data_center_positions_previous[j].split(' '))
				if x_info[required_particles[i]] == temp[0]:
					xp.append(np.float64(temp[0]))
					yp.append(np.float64(temp[1]))
					xpr.append(np.float64(temp[2]))
					ypr.append(np.float64(temp[3]))
					rad.append(np.float64(temp[2]) - np.float64(temp[0]))
					
			# --------------------------------------------------------------------------- #
					
			# Once the group center information is obtained, the node coordinates can be accumulated from various files. 
			# The node and corresponding temperature data can be extracted at the same time.
			
			if required_groups[i] == 'Particles':
				with open('../../MDPM_'+str(timestep_switch-1)+'/ABAQUS/RESULTS/Node'+str(len(all_groups)-1)+'.txt') as file:
					data_node_previous = file.read()
					
				with open('../../MDPM_'+str(timestep_switch-1)+'/ABAQUS/RESULTS/Temp'+str(len(all_groups)-1)+'.txt') as file:
					temp_data = file.read()
			else:
				with open('../../MDPM_'+str(timestep_switch-1)+'/ABAQUS/RESULTS/Node'+required_groups_numbers[i]+'.txt') as file:
					data_node_previous = file.read()
					
				with open('../../MDPM_'+str(timestep_switch-1)+'/ABAQUS/RESULTS/Temp'+required_groups_numbers[i]+'.txt') as file:
					temp_data = file.read()
					
			temp_data = temp_data.split('\n')
					
			data_node_previous = data_node_previous.split('\n')
			
			# --------------------------------------------------------------------------- #
			
			# Separate node data
			
			x1 = []
			y1 = []
			
			for j in range(len(data_node_previous)-1):
				x1.append(np.float64(data_node_previous[j].split(',')[1]))
				y1.append(np.float64(data_node_previous[j].split(',')[2]))
				
			# --------------------------------------------------------------------------- #
			
			# Sort node data according to particles
			
			initial_list = []
			node_list = []
			temp_list = []
			for j in range(len(x1)):
				if compare(x1[j], y1[j], xp[i], yp[i], (xpr[i]-xp[i])*1.01, 0) == -1:
					initial_list.append([x1[j], y1[j]])
					node_list.append(j)
					temp_list.append(temp_data[j])
			grouped_node_list_previous.append(node_list)
			grouped_temperature_list_previous.append(temp_list)
			grouped_particle_list_previous.append(initial_list)
			
			# --------------------------------------------------------------------------- #
			
			# Get x, y information for the corresponding noce data
			
			particle1x = []
			particle1y = []
			for j in range(len(grouped_particle_list_previous[i])):
				particle1x.append(grouped_particle_list_previous[i][j][0])		# Previous node data
				particle1y.append(grouped_particle_list_previous[i][j][1])
			particle1x_all.append(particle1x)
			particle1y_all.append(particle1y)
			
		# --------------------------------------------------------------------------- #
		
		# For current timestep
		
		grouped_particle_list_current = []
		grouped_node_list_current = []

		for j in range(len(xpn)):
			initial_list = []
			node_list = []
			for i in range(len(x)):
				if compare(x[i], y[i], xpn[j], ypn[j], (xprn[j]-xpn[j])*1.01, 0) == -1:
					initial_list.append([x[i], y[i]])
					node_list.append(i)
			grouped_node_list_current.append(node_list)
			grouped_particle_list_current.append(initial_list)
			
		# --------------------------------------------------------------------------- #
			
		# For every particle in previous timestep, expand at origin with the radius of the new particle and
		# assign concentration.
		
		particle2x_all = []
		particle2y_all = []
				
		for i in range(len(grouped_particle_list_current)):
			particle2x = []
			particle2y = []
			for j in range(len(grouped_particle_list_current[i])):
				particle2x.append(grouped_particle_list_current[i][j][0])		# Current node data
				particle2y.append(grouped_particle_list_current[i][j][1])
			particle2x_all.append(particle2x)
			particle2y_all.append(particle2y)
		
		# Obtain average of particles at x and y and place particles at origin
		
		for i in range(len(particle2x_all)):
			xavg = np.average(particle2x_all[i])
			yavg = np.average(particle2y_all[i])
			for j in range(len(grouped_particle_list_current[i])):
				grouped_particle_list_current[i][j][0] = grouped_particle_list_current[i][j][0] - xavg
				grouped_particle_list_current[i][j][1] = grouped_particle_list_current[i][j][1] - yavg
			
		info_update('Obtained Node and Concentration information from both current and previous timestep...')
			
		# --------------------------------------------------------------------------- #
			
		# Loop for all particles from previous timestep. These particles will be expanded to match the
		# radius of the new particle. This is done so that the concentration from the previous timestep
		# can be assigned to the current timestep as initial condition.
		
		values_already_assigned = []
		
		group_assigned = []
		
		group_temp_assigned = []
			
		for i in range(len(particle1x_all)):
			
			info_update('Running comparison for particle: '+str(i))
			
			xdiff = []
			ydiff = []
			
			xavg = np.average(particle1x_all[i])						# Obtain average of all nodes in x
			yavg = np.average(particle1y_all[i])						# Obtain average of all nodes in y
			
			# --------------------------------------------------------------------------- #
			
			# Subtracting the x and y node data from the average will place the particle at the origin.
			
			for j in range(len(particle1x_all[i])):
				xdiff.append(particle1x_all[i][j] - xavg)				
				ydiff.append(particle1y_all[i][j] - yavg)
				
			# --------------------------------------------------------------------------- #
				
			# Convert to floating point data for further manipulation.
			
			xdiff = np.float64(xdiff)									
			ydiff = np.float64(ydiff)
			
			# --------------------------------------------------------------------------- #
			
			# Convert cartesian to polar and vice versa
			
			rho, theta = cart2pol(xdiff, ydiff)							# Convert data to polar coordinates 
			
			# --------------------------------------------------------------------------- #
			
			# In order to know how much the particle has expanded the script expansion.py needs to be executed. 
			
			ratio = radn[i]/rad[i]										# Obtain new radius from odb file
			
			rho = rho*ratio												# Multiplying the rho value with the ratio will make the radius of the particle at previous and current timestep equal. 
			
			xmod, ymod = pol2cart(rho, theta)							# Convert data to cartesian coordinates
			
			# --------------------------------------------------------------------------- #
			
			# Adding the average back will move the particle at the acutal location. 
			
			#xmod = xmod + xavg
			#ymod = ymod + yavg
			
			assigned_conc_all = []
			
			assigned_temp_averaged = []
			
			for j in range(len(grouped_particle_list_current[i])):
				assigned_conc = []
				assigned_temp = []
				for k in range(len(xmod)):
					if compare(xmod[k], ymod[k], grouped_particle_list_current[i][j][0], grouped_particle_list_current[i][j][1], radn[i]*0.01,0) == -1:
						assigned_conc.append(k)
						assigned_temp.append(grouped_temperature_list_previous[i][k])
				if len(assigned_temp) < 1:
					increment = 0.01
					while True:
						for k in range(len(xmod)):
							if compare(xmod[k], ymod[k], grouped_particle_list_current[i][j][0], grouped_particle_list_current[i][j][1], radn[i]*(0.01+increment),0) == -1:
								assigned_conc.append(k)
								assigned_temp.append(grouped_temperature_list_previous[i][k])
						if len(assigned_temp) > 1:
							break
							info_update('Increment loop break...')
						else:
							increment += 0.01
							#info_update('Increment loop: '+str(increment))
				if len(assigned_temp) > 1:
					assigned_temp_averaged.append(np.average(np.float64(assigned_temp)))
				else:
					assigned_temp_averaged.append(np.float64(assigned_temp)[0])
				assigned_conc_all.append(assigned_conc)
			group_temp_assigned.append(assigned_temp_averaged)
			group_assigned.append(assigned_conc_all)
			
		# --------------------------------------------------------------------------- #
			
		# Flatten out arrays and weed out repeated values
		
		particle2x_flatten = [item for sublist in particle2x_all for item in sublist]
		
		grouped_node_list_current_flattened = np.array([item for sublist in grouped_node_list_current for item in sublist])
		
		repeated_x = []
		repeated_id = []
		
		for i in range(len(particle2x_flatten)):
			#if not str(particle2x_flatten[i]) in repeated_x:
				repeated_x.append(str(particle2x_flatten[i]))
				repeated_id.append(i)
				
		info_update('Repeated concentration values removed...')
		
		group_temp_assigned_flattened = np.array([item for sublist in group_temp_assigned for item in sublist])
		
		group_temp_assigned_reordered = group_temp_assigned_flattened[np.array(repeated_id)]
		
		grouped_node_list_current_reordered = grouped_node_list_current_flattened[np.array(repeated_id)]
		
		for i in range(len(grouped_node_list_current_reordered)):
			finit.write(str(grouped_node_list_current_reordered[i]+1)+','+str(group_temp_assigned_reordered[i]))
			finit.write('\n')

	        for entry,value in enumerate(bnodes_all):
			famplitude.write('*Amplitude, name=Amp-'+str(value)+', definition=SMOOTH STEP\n')
			temp_in_previous = str(group_temp_assigned_reordered[int(np.where(grouped_node_list_current_reordered==value-1)[0][0])-1])
			famplitude.write('0.0,             '+temp_in_previous+',              0.05,             1.\n') # charge -discharge change final value to 1 or 0
		famplitude.close()	

	finit.close()
	
	
	info_update('All files written...')
	
	# --------------------------------------------------------------------------- #
		
	# Write step data
	
	fnew.write('\n*Step, name=Step-1, nlgeom=NO,inc=1500,UNSYMM=YES\n')
	fnew.write('*Coupled Temperature-displacement, creep=none\n')
	if timestep_switch < 2: 
		fnew.write('0.005,0.4\n')#,0.01,0.01
	else:
		fnew.write('0.005,0.4\n')#,0.01,0.01\n')
	
	info_update('Step data written...')

	# --------------------------------------------------------------------------- #

	# Write Boundary condition - keyword

	fnew.write('*Boundary\n')
	fnew.write(set_val + ',1,2\n')
	
	info_update('BC properties written...')

	# --------------------------------------------------------------------------- #

	# Write the next BC - Left part of domain

	# Check if list contains values
	if timestep_switch < 2 :
		if left_concentration_bc:
			
			fnew.write('*Boundary,amplitude=Amp-1\n')
		
			fnew.write(set_val2 + ',11,11,1\n')
			#fnew.write(set_val2 + ',11,11,0\n')
		
			info_update('Left BC properties written...')
	else:
		for node in bnodes_all:
			fnew.write('*Boundary,amplitude=Amp-'+str(node)+'\n')
			fnew.write(str(node)+',11,11,1\n')
			#fnew.write(str(node)+',11,11,0\n')
		info_update('Left BC properties written...')	
	
	# --------------------------------------------------------------------------- #
				
	# Write remaining data
	
	fnew.write('*Restart, write, frequency=0\n\
*Output, field, variable=PRESELECT,frequency=999999\n\
*Output, history, variable=PRESELECT\n\
*End Step\n')

	info_update('Restart data written...')
	info_update('Field output data written...')
	info_update('History output data written...')

	fnew.close()
	
	# --------------------------------------------------------------------------- #
	
	# Modify UVARM file with current element information
	
	with open('sid_aba_connec_uvarm.f') as file:
		uvarm_data = file.read()
		
	uvarm_data = uvarm_data.split('\n')
	
	uvarm_data[26] = "!      parameter(numElem="+str(count_uvarm)+")"
	
	fuvarm_new = open('sid_aba_connec_uvarm_mod.f', 'w+')
	
	for i in uvarm_data:
		fuvarm_new.write(i)
		fuvarm_new.write('\n')
		
	fuvarm_new.close()
	
	info_update('Modified UVARM file...')
	
import ConfigParser
config = ConfigParser.ConfigParser()
config.readfp(open(r'/home/pramod/matlab_wrapper/python/config.c')) # config file location
info_file = config.get('Details', 'info_file')
modinp(info_file)

