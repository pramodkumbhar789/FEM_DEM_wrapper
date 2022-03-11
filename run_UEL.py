# Developed by  
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.


################################ Purpose #########################################
# Automation of the execution of the FEM.
##################################################################################


def uel(username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,timestep):
	
	global q_uel
	
	# --------------------------------------------------------------------------- #
	
	''' 
	
	This function is responsible for running the modified inp files. 
		
	REQUIREMENTS:
	
	-> ABAQUS inp files (modified).
		
	USAGE:
	
	-> Can be executed through wrapper_main.py
	-> Can be run standalone. In this case, please add uel() at the end 
	of the script.
		
	'''
	
	# --------------------------------------------------------------------------- #
	
	# Import modules

	import numpy as np
	from time import strftime
	import os
	from Queue import Queue
	from threading import Thread
	from threading import Lock
	
	# --------------------------------------------------------------------------- #

	#global username,wrapper_path, info_file, ABAQUS_path,project_name,project_path,timestep 
	# --------------------------------------------------------------------------- #
	
	# Define function to update info file
	
	def info_update(update_line):
		Info_file = open(info_file, 'a')
		Info_file.write(strftime('[%H:%M:%S]'+'\t\t'+update_line+'\n'))
		Info_file.close()
		
	
	# --------------------------------------------------------------------------- #
				
	# Obtain the recent timestep by seeking to the last timestep.

	timestep_last = timestep
	
	# --------------------------------------------------------------------------- #
	
	# Navigate to ABAQUS folder with inp files for current timestep
	
	os.chdir(project_path + '/' + 'MDPM_' + str(timestep_last) +'/ABAQUS')
	
	# --------------------------------------------------------------------------- #
	
	# Obtain list of all inp files
	
	inp_file_list = [f for f in os.listdir(os.getcwd()) if f.endswith('.inp')]
	
	# --------------------------------------------------------------------------- #
	
	# Sort the file list 
	
	sorted_inp_file_list = []
	
	for i in range(len(inp_file_list)):
		sorted_inp_file_list.append('Job_'+str(i)+'.inp')
		
	# --------------------------------------------------------------------------- #
	
	# Total number of files to be individually run
	
	files_list = os.listdir('../')								# Get list of all files in the folder
	
	# --------------------------------------------------------------------------- #
	
	# Sort the files list to avoid wrong numbering
	
	sort_counter = 0													# This ensures that the numbering is ascending
	
	sorted_files_list = []
	
	for i in files_list:
		if 'Group' in i:
			sorted_files_list.append('Group'+str(sort_counter)+'.txt')
			sort_counter += 1
	for i in files_list:												# Appending separately to avoid Particles.txt being executed inbetween
		if 'Particle' in i:
			sorted_files_list.append(i)
	
	# --------------------------------------------------------------------------- #
		
	# Copy modify_inp.py and expansion.py scripts to current location
		
	os.system('cp '+ wrapper_path + 'modify_inp.py .')
	os.system('cp '+ wrapper_path + 'expansion.py .')
	os.system('cp '+ wrapper_path + 'abaqus_v6.env .')
	os.system('cp '+ wrapper_path + 'boundary.py .')
	os.system('cp '+ wrapper_path + 'sid_aba_connec_uvarm.f .')
	os.system('cp '+ wrapper_path + 'tecplot_combine.py .')
	
	info_update('Copied modify_inp.py, expansion.py, abaqus_v6.env, sid_aba_connec_uvarm.f, tecplot_combine.py')
	
	# --------------------------------------------------------------------------- #
	
	# Initiate threads and queues 
	
	q_uel = Queue(maxsize=0)											# Sets queue count to infinity

	threads_uel = 1

	# --------------------------------------------------------------------------- #
	
	# Assign jobs to queue
	
	lock = Lock()
	
	for i in range(len(sorted_inp_file_list)):
		q_uel.put((i, i))
		
	# --------------------------------------------------------------------------- #
	
	# The scripts modify_inp.py and expansion.py is executed for all of the Job files.
	
	info_update('Modifying inp_files...')
	
	def process(q_uel):
		
		while not q_uel.empty():
			
			lock.acquire()
			
			try:
		
				work = q_uel.get()
				
				print sorted_inp_file_list[work[1]]
			
				# Modify the script modify_inp.py
			
				with open('modify_inp.py') as file:
					data = file.read()
					
				data = data.split('\n')
				
				data[74] = '\ttimestep_switch = '+ str(timestep_last) 															# Set timestep_switch for appropriate processing of data
				data[142] = "\tinp_file = 'Job_"+str(work[1])+".inp'"													# Modify the inp file to be read
				data[155] = "\tfn = open('Node"+str(work[1])+".txt'"+",'w+')"											# Node file numbering is kept similar to Job numbering
				data[156] = "\tfe = open('Element"+str(work[1])+".txt'"+",'w+')"										# Element file numbering is kept similar to Job numbering 
				data[157] = "\tfuvarm = open('Element_uvarm"+str(work[1])+".txt'"+",'w+')"								# Element file numbering for uvarm
				data[278] = "\tfnew = open('Job__"+str(work[1])+"s.inp'"+",'w+')"										# New Job file to be written. An 's' is added at the end to signify the difference
				data[308] = "\t\t\tnode_list[count] = node_list[count] + ', input=Node"+str(work[1])+".txt'"			# Select the input as the newly created node file
				data[313] = "\t\t\tfnew.write('*Node,NSET=all,input=Node"+str(work[1])+".txt')"							# Select the input as the newly created node file
				data[328] = "\t\t\telement_list[count] = element_list[count] + ', input=element"+str(work[1])+".txt'"	# Select the input as the newly created element file
				data[333] = "\t\t\tfnew.write('*Element, type=U1, Elset=ALL,input=Element"+str(work[1])+".txt')"		# Select the input as the newly created element file
				data[360] = "		fnew.write('*include, input=Element_uvarm"+str(work[1])+".txt')"					# Select the element file for UVARM
				if work[1] == len(sorted_inp_file_list) - 1:
					if 'Particles' in str(sorted_files_list[-1]):
						data[377] = "\twith open('../Particles.txt') as file:" 											# Select the Group data corresponding to the job file
					else:
						data[377] = "\twith open('../Group"+str(work[1])+".txt') as file:"
				else:
					data[377] = "\twith open('../Group"+str(work[1])+".txt') as file:" 									# Select the Group data corresponding to the job file
				data[399] = "\twith open('Node"+str(work[1])+".txt') as file:"											# Select the previously created node data
				if work[1] == len(sorted_inp_file_list)-1:
					data[421] = "	particle_data = 'yes'"
				else:
					data[421] = "	particle_data = 'no'"
				data[483] = "\tbnodes = boundary_nodes("+str(work[1])+")" 
				data[558] = "\t\tfnew.write('*include,input=Amp"+str(work[1])+".txt\\n')"
				data[564] = "\tfinit = open('Initial"+str(work[1])+".txt', 'w+')"										# Create file for storing initial condition data
				data[565] = "\tfnew.write('*include,input=Initial"+str(work[1])+".txt')"								# Point to initial data. Remove for timestep > 1
				data[581] = "\t\tfamplitude = open('Amp"+str(work[1])+".txt', 'w+')"								# Point to initial data. Remove for timestep > 1
				new_py_file = open('modify_inp_mod'+str(work[1])+'.py', 'w+')											# Create new file for storing the modified script
					
				for k in range(len(data)):
					new_py_file.write(data[k])
					new_py_file.write('\n')
					
				new_py_file.close()
				
				info_update('Modified python file modify_inp for group '+ str(work[1]))
				
				info_update('Executing modify_inp_mod for group '+ str(work[1]))
				
				os.system('python modify_inp_mod'+str(work[1])+'.py')
			
			finally:
				
				lock.release()
			info_update('Execution started the abaqus uel'+'Job__'+str(work[1])+'s ')			
			os.system(ABAQUS_path + ' job=Job__'+str(work[1])+'s user=sid_aba_connec_uvarm_mod double inter >> log%d.txt'%work[1])
			info_update('Execution ended the abaqus uel'+'Job__'+str(work[1])+'s ')
			q_uel.task_done()
		
		return True
		
	# --------------------------------------------------------------------------- #
	
	# Initialize workers
	
	for i in range(threads_uel):
		
		worker = Thread(target=process, args=(q_uel,))
		
		worker.setDaemon(True)
		
		worker.start()
		
	q_uel.join()
	
	# --------------------------------------------------------------------------- #
	
	# Copy all files to RESULTS folder for further maniputation
		
	os.mkdir('RESULTS')
	
	os.chdir(project_path + '/' + 'MDPM_' + str(timestep_last) +'/ABAQUS/RESULTS/')
	
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/*.odb '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/RESULTS/')
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/Job__*s.inp '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/RESULTS/')
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/Element*.txt '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/RESULTS/')
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/expansion.py '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/RESULTS/')
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/Initial*.txt '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/RESULTS/')
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/Node*.txt '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/RESULTS/')
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/tecplot_combine.py '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/RESULTS/')
	
	info_update('Moved files Job__*s.inp, *.odb, Element*.txt, Node*.txt, expansion.py, tecplot_combine.py  to RESULTS folder...')
	#info_update('Moved files Job__*s.inp to RESULTS folder...')
	#info_update('Moved files Element*.txt to RESULTS folder...')
	#info_update('Moved files Initial*.txt to RESULTS folder...')
	#info_update('Moved files Node*.txt to RESULTS folder...')
	#info_update('Moved files expansion.py to RESULTS folder...')
	#info_update('Moved files tecplot_combine.py to RESULTS folder...')
	
	# --------------------------------------------------------------------------- #
	
	# Write all volume data to volume_data.txt
	
	fvolume_all = open('volume_data.txt', 'w+')
	
	info_update('Writing volume data to volume_data.txt...')
	
	# --------------------------------------------------------------------------- #
	
	# Initiate threads and queues 
	
	q_expansion = Queue(maxsize=0)											# Sets queue count to infinity

	threads_expansion = 1

	# --------------------------------------------------------------------------- #
	
	# Assign jobs to queue
	
	lock = Lock()
	
	for i in range(len(sorted_inp_file_list)):
		
		q_expansion.put((i, i))
		
	# --------------------------------------------------------------------------- #
	
	# Run ABAQUS Macro for extrating information from odb files
	
	info_update('Modifying file expansion.py...')
	
	def expansion_process(q_expansion):
		
		while not q_expansion.empty():
			
			lock.acquire()
			
			try:
				
				work = q_expansion.get()
	
	#for i in range(len(sorted_inp_file_list)):
		
				with open('expansion.py') as file:
					data = file.read()
					
				data = data.split('\n')
				
				data[171] = "\tname=['Job__"+str(work[1])+"s']"
				
				data[216] = "\telement_file = 'Element"+str(work[1])+".txt'"
				
				if str(work[1]) == str(len(sorted_inp_file_list)-1):
					
					if 'Particles' in str(sorted_files_list[-1]):
						
						data[374] = "\twith open('../../Particles.txt') as file:" 											# Select the Group data corresponding to the job file
					else:
						data[374] = "\twith open('../../Group"+str(work[1])+".txt') as file:"
						
				else:
				
					data[374] = "\twith open('../../Group"+str(work[1])+".txt') as file:"
					
				data[403] = "\tfvolume = open('volume_data"+str(work[1])+".txt', 'w+')"
				
				data[438] = "\tfile_open = open('Temp"+str(work[1])+".txt', 'w+')"
				
				data[444] = "\tfile_open1 = open('disp"+str(work[1])+".txt', 'w+')"
				
				data[450] = "\tfile_open2 = open('stress"+str(work[1])+".txt', 'w+')"
				
				data[456] = "\tfile_open3 = open('strain"+str(work[1])+".txt', 'w+')"
				
				expansion_mod = open('expansion_mod'+str(work[1])+'.py', 'w+')
				
				for j in data:
					expansion_mod.write(j)
					expansion_mod.write('\n')
				
				expansion_mod.close()
			
			finally:
				
				lock.release()
		
			#info_update('Executing file expansion_mod.py for group '+str(work[1]))
			
			os.system(ABAQUS_path + ' cae noGUI=expansion_mod'+str(work[1])+'.py')
			
			q_expansion.task_done()
	
	# --------------------------------------------------------------------------- #
	
	# Initialize workers
	
	for i in range(threads_expansion):
		
		worker = Thread(target=expansion_process, args=(q_expansion,))
		
		worker.setDaemon(True)
		
		worker.start()
		
	q_expansion.join()
	
	# --------------------------------------------------------------------------- #
	
	for i in range(len(sorted_inp_file_list)):
		
		with open('volume_data'+str(i)+'.txt') as file:
			for line in file:
				fvolume_all.write(line)
	
	fvolume_all.close()
	
	info_update('Volume data written...')
	
	# --------------------------------------------------------------------------- #
	
	# Combine all odb information
	
	info_update('Running tecplot_combine to combine data from all odb files for visualization...')
	
	os.system('python tecplot_combine.py')
	
	info_update('Tecplot data written...')
	
	return timestep
		
