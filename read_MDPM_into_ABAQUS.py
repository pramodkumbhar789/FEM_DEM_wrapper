# Developed by  
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.


################################ Purpose #########################################
# For reading the MercuryDPM data into ABAQUS for subsequent meshing
##################################################################################


def mdpm2abaqus(username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,timestep):
	
	#global data
	
	# --------------------------------------------------------------------------- #
	
	''' 
	
	This function is responsible for reading the MercuryDPM data into ABAQUS 
	for subsequent meshing. 
		
	REQUIREMENTS:
	
	-> MercuryDPM data files.
		
	USAGE:
	
	-> Can be executed through wrapper_main.py
	-> Can be run standalone. In this case, please add mdpm2abaqus() at the end 
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
				
	#global username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,timestep 
	
	# --------------------------------------------------------------------------- #
	
	# Define function to update info file
	
	def info_update(update_line):
		Info_file = open(info_file, 'a')
		Info_file.write(strftime('[%H:%M:%S]'+'\t\t'+update_line+'\n'))
		Info_file.close()
	
	# --------------------------------------------------------------------------- #
	
	timestep_last = timestep
	
	# --------------------------------------------------------------------------- #
	
	# Total number of files to be individually run
	
	files_list = os.listdir(os.getcwd())								# Get list of all files in the folder
	
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
	
	# Copy abaqus_exec.py file for modification and execution
	
	os.system('cp -i '+ wrapper_path + 'abaqus_exec.py '+ project_path + '/MDPM_' + str(timestep_last) + '/.')
	
	info_update('Time step: '+ str(timestep_last) )
	
	with open('abaqus_exec.py') as file:								# Needed for dynamic editing. Explanation is provided below
		pydata = file.read()
		
	pydata = pydata.split('\n')
	
	info_update('Created python file for dynamic editing...')
	
	# --------------------------------------------------------------------------- #
	
	# Initiate threads and queues for parallel processing.
	
	q_mesh = Queue(maxsize=0)											# Set number of queues to infinity (0 corresponds to infinity)
	
	threads_mesh = 1													# Initiate number of threads to run simultaneously
	
	info_update('Number of threads set to: '+ str(threads_mesh))
	
	# --------------------------------------------------------------------------- #
	
	# Assign jobs to queue
	
	for mesh_count in range(len(sorted_files_list)):
		
		q_mesh.put((mesh_count, sorted_files_list[mesh_count]))			# Data from sorted_files_list is stored as a tuple with an index
		
	len_files = len(sorted_files_list)
		
	info_update('Jobs assigned to queue...')
	
	# --------------------------------------------------------------------------- #
		
	def check_queue(file_to_check, mesh_count, work_data):
		add_queue = 0
		cae_file_list = [f for f in os.listdir(os.getcwd()) if f.endswith('.cae')]
		group_file_list = [f for f in os.listdir(os.getcwd()) if f.endswith('.txt')]
		for j in cae_file_list:
			if str(file_to_check) in j:
				add_queue = 0
				break
			else:
				add_queue = 1
		if add_queue == 1:
			
			print 'One of the threads initialized failed. Please reduce the number of threads to be run.'
			os.system('kill -TSTP '+str(os.getpid()))
			#mesh_count += 1
			#q_mesh.put((int(mesh_count), work_data))
	# --------------------------------------------------------------------------- #
	
	# Define process to run
	
	lock = Lock()
	
	def process(q_mesh, len_files):
		
		while not q_mesh.empty():										# Check if queue is empty
			
			lock.acquire()
			
			try:
			
				work = q_mesh.get()											# Assign work to be done
				
				if 'Particles' in work[1]:
					
					file_number = len_files-1
				
				else:
				
					file_number = work[1].split('p')[1].split('.txt')[0]
			
				# Get the minimum radius of the group. Used for mesh size determination
				
				radius = []
				
				with open(work[1]) as file:
					data = file.read()
					
				print work[1]
					
				data = data.split('\n')
				
				for j in range(len(data) - 1):
					temp = filter(None, data[j].split(' '))
					radius.append(np.float64(temp[2]) - np.float64(temp[0]))
					
				radius_min = np.average(radius)

				# Edit macro script for reading into ABAQUS. 
				# Dynamic editing is done as ABAQUS has problems with passing command line arguments. 
				
				#pydata[43] = '\tmesh_size = ' + str(np.float64(radius_min)/4) # Edit mesh size before it was radius_min/4
				#pydata[44] = '\tjob_name = ' + "'Job_" + str(file_number) + "'" 	# Edit job name
				#pydata[45] = "\tfile_name = '"+ work[1] +"' "					# Edit file name to be read
				#pydata[110] = "\tmdb.Job(name='Job_"+str(file_number)+"', model='Model-1', description='', type=ANALYSIS,"
				#pydata[117] = "\tmdb.jobs['Job_"+str(file_number)+"'].writeInput(consistencyChecking=OFF)"
				#pydata[119] = "\tmdb.saveAs('model_" + str(file_number) + ".cae')"	# Save cae file so that the corresponding data can be viewed later
				
				mesh_size_file = open('mesh_sizes.txt', 'a')				# Create new file for storing the modified script
				
				mesh_size_file.write(work[1])
				mesh_size_file.write('\t')
				mesh_size_file.write(str(np.float64(radius_min)/4))
				mesh_size_file.write('\n')
					
				mesh_size_file.close()
				
			finally:
				
				lock.release()
			
			check_queue(int(file_number), mesh_count, work[1])
			
			q_mesh.task_done()
		
		return True
	
	# --------------------------------------------------------------------------- #
	
	# Initialize workers
	
	for i in range(threads_mesh):
		
		worker = Thread(target=process, args=(q_mesh, len_files))
		
		worker.setDaemon(True)
		
		worker.start()
		
	q_mesh.join()
		
	# --------------------------------------------------------------------------- #
	print 'In read_MDPM_into_ABAQUS'
		
	os.system(ABAQUS_path +' cae noGUI=abaqus_exec.py')
			
	info_update('Meshed all the groups')
			
	# Move all abaqus files to ABAQUS folder
	
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/*.jnl '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/')
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/*.cae '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/')
	os.system('mv '+ project_path + '/MDPM_' + str(timestep_last) + '/*.inp '+ project_path + '/MDPM_' + str(timestep_last) + '/ABAQUS/')
	
	info_update('Meshing complete ...')
	
	return timestep
#mdpm2abaqus()
