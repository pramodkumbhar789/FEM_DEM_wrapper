# Developed by  
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.


################################ Purpose #########################################
# Formation of the sub-domains based on the extent of the overlap
##################################################################################



def mdpm2group(username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,timestep):
	
	# Uncomment the following line for debugging
	
	# global sorted_files_list, x, x1, y, radius, data, particle_list, grouped_list_particle_id
	
	# --------------------------------------------------------------------------- #
	
	''' 
	
	This function is responsible for reading the MercuryDPM data and splitting it 
	into appropriate groups.
	
	The particles which intersect are kept in groups while those which do not are
	kept in a separate file. 
		
	REQUIREMENTS:
	
	-> MercuryDPM data file.
		
	USAGE:
	
	-> Can be executed through wrapper_main.py
	-> Can be run standalone. In this case, please add mdpm2abaqus() at the end 
	of the script.
		
	'''
	
	# --------------------------------------------------------------------------- #
	
	# Import modules
	
	import os
	import numpy as np
	import matplotlib.pyplot as plt
	from time import strftime
	
	# --------------------------------------------------------------------------- #
	#global username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,timestep	
	# Initialize data lists

	particle_list = []
	grouped_list_particle_id = []
	
		
	def info_update(update_line):
		Info_file = open(info_file, 'a')
		Info_file.write(strftime('[%H:%M:%S]'+'\t\t'+update_line+'\n'))
		Info_file.close()
	
	# --------------------------------------------------------------------------- #
				
	# Obtain the recent timestep by seeking to the last timestep.
	
	timestep_last = timestep
	print timestep,'in read_data_output'
	info_update('Time step: '+str(timestep_last)+'...')
	
	if timestep_last == 1:										# Only for the first timestep the data at the beginning is read. 
		read_data = 'first'
	else:
		read_data = 'last' 									# In this case, the data at the last time step is read. 
		
	# --------------------------------------------------------------------------- #
				
	# Obtain the data file from the MercuryDPM folder
	
	if timestep_last == 1:
	
		MDPM_path = '/home/'+username+'/MercuryDPM/MercuryBuild/Drivers/'+project_name	# Path to the created project directory
	
	else:
		
		MDPM_path = '/home/'+username+'/MercuryDPM/MercuryBuild/Drivers/'+project_name + '_' +str(timestep_last)
	
	info_update('Changing project directory to:'+MDPM_path+'...')
	
	os.chdir(MDPM_path)						# Change directory to access all files

	for i in os.listdir(os.getcwd()):									# Find the data file by doing a scan of all files in the directory
		if '.data' in i:
			required_file = i

			
	info_update('Found and read the appropriate data file in MDPM folder...')

	with open(required_file) as file:									# Read in the data file
		data = file.read()	

	data = data.split('\n')												# Split along new lines
	
	no_of_particles = int(data[0].split(' ')[0])						# Get the intial number of particles
        print 'timestep',timestep,no_of_particles
	
	info_update('Data splitting will be done according to timestep_last...')
	
	data = data[-no_of_particles-1:-1]									# Get the last set of data
	
	x = []																# Initialize data storage lists
	y = []
	radius = []
	
	#print data

	for i in range(len(data)):											# Split and append position x, y and radius data
		data_split = data[i].split(' ');fact=1e3; # earlier factor was 1e6 Edited by Pramod
		x.append(np.float64(data_split[0])*fact)
		y.append(np.float64(data_split[1])*fact)
		radius.append(np.float64(data_split[4])*fact)
		
	info_update('Data split done...')

	def compare(x1, y1, x2, y2, r1, r2):								# Function definition for finding circles which intersect
		distsq = np.sqrt((x1-x2)**2 + (y1-y2)**2)						
		radsum = r1+r2
		
		if distsq < 0.98*radsum:# or distsq == radsum: 		# If the distance between the centeres is less than the sum of their radii, they intersect
			return -1
			
	# --------------------------------------------------------------------------- #
			
	# The following part of the code separates the particles to groups

	info_update('Sorting particle into groups...')
	
	for i in range(len(x)):
		grouped_list_particle_id_flatten = [item for sublist in grouped_list_particle_id for item in sublist]
		if not i in grouped_list_particle_id_flatten:
			particle_list = []
			trial_list = []
			trial = i
			#print trial
			def neighbor_find(x, y, radius, particle_list, trial):
				for j in range(len(x)):
					if compare(x[trial], y[trial], x[j], y[j], radius[trial], radius[j]) == -1:
						if not j in particle_list:
							particle_list.append(j)
			neighbor_find(x, y, radius, particle_list, trial)
			trial_list.append(trial)
			while True:
				if len(trial_list) == len(particle_list):
					break
				else:
					for k in range(len(particle_list)):
						if not particle_list[k] in trial_list:
							trial = particle_list[k]
							neighbor_find(x, y, radius, particle_list, trial)
							trial_list.append(trial)
						else:
							pass
			grouped_list_particle_id.append(particle_list)			
	
	info_update('Grouping done...')
		
	info_update('Writing particle data...')
	
	group_counter = 0
	f1 = open('Particles.txt', 'w+')		# This file stores particles which are single
	info_update('Created Particles.txt...')
	particle_counter = 0
	
	for i in range(len(grouped_list_particle_id)):
		if len(grouped_list_particle_id[i]) > 1:
			f = open('Group%d.txt'%group_counter, 'w+')					# Files are created sequentially to store grouped particle data
			info_update('Created Group%d.txt...'%group_counter)
			group_counter += 1
			for j in range(len(grouped_list_particle_id[i])):
				f.write((str(x[grouped_list_particle_id[i][j]]).ljust(10) + ' ' + str(y[grouped_list_particle_id[i][j]]).ljust(10) + ' ' + str(x[grouped_list_particle_id[i][j]] + radius[grouped_list_particle_id[i][j]]).ljust(10) + ' ' + str(y[grouped_list_particle_id[i][j]])  + '\n'))
				#f.write((str(x[grouped_list_particle_id[i][j]]).ljust(10) + '\t ' + str(y[grouped_list_particle_id[i][j]]).ljust(10) + '\t ' + str(x[grouped_list_particle_id[i][j]] + radius[grouped_list_particle_id[i][j]]).ljust(10) + '\t ' + str(y[grouped_list_particle_id[i][j]])  + '\n'))
			f.close()
		else:		
			#f1.write((str(x[grouped_list_particle_id[i][0]]).ljust(10) + '\t ' + str(y[grouped_list_particle_id[i][0]]).ljust(10) + '\t ' + str(x[grouped_list_particle_id[i][0]] + radius[grouped_list_particle_id[i][0]]).ljust(10) + '\t ' + str(y[grouped_list_particle_id[i][0]]) + '\n'))
			f1.write((str(x[grouped_list_particle_id[i][0]]).ljust(10) + ' ' + str(y[grouped_list_particle_id[i][0]]).ljust(10) + ' ' + str(x[grouped_list_particle_id[i][0]] + radius[grouped_list_particle_id[i][0]]).ljust(10) + ' ' + str(y[grouped_list_particle_id[i][0]]) +'\n'))
			particle_counter += 1

	# --------------------------------------------------------------------------- #

	# The following code can be used if no particle groups are required and all data will be printed in the file Particles.txt

	#for i in range(len(grouped_list_particle_id)):
		#for j in range(len(grouped_list_particle_id[i])):
			#f1.write((str(x[grouped_list_particle_id[i][j]]).ljust(10) + '\t ' + str(y[grouped_list_particle_id[i][j]]).ljust(10) + '\t ' + str(x[grouped_list_particle_id[i][j]] + radius[grouped_list_particle_id[i][j]]).ljust(10) + '\t ' + str(y[grouped_list_particle_id[i][j]] + radius[grouped_list_particle_id[i][j]]).ljust(10) + '\n'))
	
	f1.close()
	
	info_update('All particle data has been written')

	os.mkdir(project_path + '/MDPM_' + str(timestep_last) )
	
	info_update('Created new directory MDPM_'+ str(timestep_last) )
	
	info_update('% '+ project_path + '/MDPM_' + str(timestep_last) )
	
	if particle_counter == 0 and group_counter > 0:
	
		os.system('mv Group*.txt '+ project_path + '/MDPM_' + str(timestep_last) )  
	
	elif group_counter == 0 and particle_counter > 0:
		
		os.system('mv Particles.txt '+ project_path + '/MDPM_' + str(timestep_last) )  
	
	elif group_counter > 0 and particle_counter > 0:
		
		os.system('mv Group*.txt Particles.txt '+ project_path + '/MDPM_' + str(timestep_last) )
	
	info_update('All particle data has been moved to project directory')
	print 'in contactarea'
	# --------------------------------------------------------------------------- #
	
	# Write particle database
	
	info_update('Writing Particle database...')
	
	os.chdir(project_path + '/MDPM_' + str(timestep_last) )
	
	sorted_files_list = []
	
	files_list = os.listdir(os.getcwd())
	
	sort_counter = 0
	
	for i in files_list:
		if 'Group' in i:
			sorted_files_list.append('Group'+str(sort_counter)+'.txt')
			sort_counter += 1
	for i in files_list:
		if 'Particle' in i:
			sorted_files_list.append(i)
	
	particle_data = open(project_path + '/log/Particle_database' + str(timestep_last) +'.txt', 'w+')
	
	#particle_data.write(str('ID').ljust(20) + '\t' + str('x').ljust(20)+ '\t' + str('y').ljust(20)+ '\t' + str('Radius').ljust(20)+ '\t' + str('Group').ljust(20))
	particle_data.write(str('ID').ljust(20) + str('x').ljust(20) + str('y').ljust(20) + str('Radius').ljust(20) + str('Group').ljust(20))
	particle_data.write('\n')
	for i in range(len(x)):
		required_group_file = ''
		for j in range(len(sorted_files_list)):
			with open(sorted_files_list[j]) as file:
				group_data = file.read()
			group_data = group_data.split('\n')
			x1 = []
			y1 = []
			for k in range(len(group_data)-1):
				temp = filter(None, group_data[k].split(' '))
				x1.append(temp[0])
				y1.append(temp[1])
			if str(x[i]) in x1 and str(y[i]) in y1:
				if not j == len(sorted_files_list) - 1:
					required_group_file = 'Group'+str(j)
				else:
					if 'Group' in sorted_files_list[-1]:
						required_group_file = 'Group'+str(j)
					else:
						required_group_file = 'Particles'
		#particle_data.write(str(i+1).ljust(20) + '\t' +str(x[i]).ljust(20) + '\t' +str(y[i]).ljust(20) + '\t' + str(radius[i]).ljust(20) + '\t' + str(required_group_file).ljust(20))
		particle_data.write(str(i+1).ljust(20) +str(x[i]).ljust(20) +str(y[i]).ljust(20) + str(radius[i]).ljust(20) + str(required_group_file).ljust(20))
		particle_data.write('\n')
	return timestep
