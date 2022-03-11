# Developed by  
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.


################################ Purpose #########################################
# Automation of the compilation and execution of the DEM script.
##################################################################################


def cne(username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,timestep):	
	
	# --------------------------------------------------------------------------- #
	
	''' 
	
	This function is responsible for the compilation and execution of MercuryDPM.
	
	REQUIREMENTS:
	
	-> cpp file containing the parameters of the simulation.
	
	USAGE:
	
	-> Can be executed through wrapper_main.py
	-> Can be run standalone. In this case, please add cne() at the end of the script.
	
	'''
	
	# ---------------------------------------------------------------------------- #

	# Last updated: 05-06-2018

	# Import modules

	import Tkinter as tk
	from tkFileDialog import askopenfilename as ask
	from tkFileDialog import askdirectory as askdir
	import os
	import sys
	import shutil
	from time import strftime
	import numpy as np
	
	# --------------------------------------------------------------------------- #

	# Initialize

	root = tk.Tk()														# Creates a Tkinter widget. Required for Dialog box.
	root.withdraw()														# This is done in order to remove the unnecessary widget which crops up.
	current_dir = os.getcwd()											# Get the current directory
	#global username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,timestep	
	cmakefile = '/home/'+username+'/MercuryDPM/CMakeLists.txt'			# Path to CMakeLists file

	
	# --------------------------------------------------------------------------- #
	
	# Load project information from Info file	
	
	timestep = timestep + 1
	print 'Current timestep',timestep

	with open(info_file) as file:
		for line in file:
			if '!!' in line:
				new_file = line
				
	
	# --------------------------------------------------------------------------- #
	
	# Obtain the recent timestep by seeking to the last timestep.
	
	timestep_last = timestep
	
	def info_update(update_line):
		Info_file = open(info_file, 'a')
		Info_file.write(strftime('[%H:%M:%S]'+'\t\t'+update_line+'\n'))
		Info_file.close()
		
	# --------------------------------------------------------------------------- #
	
	# Clean up MercuryDPM directory to avoid errors caused by existing make targets
	
	if timestep_last == 1:
	
		print '\nCleaning MercuryDPM directory..'
		
		Mercury_source_path = '/home/'+username+'/MercuryDPM/MercurySource/Drivers/'
		Mercury_build_path = '/home/'+username+'/MercuryDPM/MercuryBuild/Drivers/'

		Default_files_source = ['UnitTests', 'CMakeLists.txt', 'CMakeFiles', 'Makefile', 'MercurySimpleDemos', 'MercuryCG', 'CTestTestfile.cmake', 'cmake_install.cmake', 'Tutorials', 'CMakeCache.txt']
		Default_files_build = ['UnitTests', 'CMakeFiles', 'Makefile', 'MercurySimpleDemos', 'MercuryCG', 'CTestTestfile.cmake', 'cmake_install.cmake', 'Tutorials']

		os.chdir(Mercury_source_path)

		files_source = os.listdir(os.getcwd())

		if len(files_source) > len(Default_files_source):
			for i in files_source:
				if i not in Default_files_source:
					shutil.rmtree(i)

		os.chdir(Mercury_build_path)

		files_build = os.listdir(os.getcwd())

		if len(files_build) > len(Default_files_build):
			for i in files_build:
				if i not in Default_files_build:
					shutil.rmtree(i)
		
		os.chdir(wrapper_path)
	
	# --------------------------------------------------------------------------- #

	# Select file
	
	if timestep_last == 1:

		File = ask(initialdir = current_dir, title = 'Select the c++ file', filetypes = (("C++","*.cpp"),("All files","*.*")))		# Allows the user to select the cpp file containing the simulation parameters.
		File_name = File.split('/')[-1]									# Obtain the file name
	
	else:
		
		new_file = new_file[4:]
		File = new_file[:-1]
		File_name = File.split('/')[-1]									# Obtain the file name
		
	print '\nSelected file: ', File_name								# Print file name
	info_update('DEM file name = '+str(File_name))	
	# --------------------------------------------------------------------------- #
	
	# Read C++ file and write domain information to Info.txt
	
	info_update('Reading C++ file...')
	
	with open(File) as file:
		for line in file:
			if 'problem.setXMax' in line:
				info_update('Domain info: XMax = ' + line.split('(')[1].split(')')[0])
			elif 'problem.setYMax' in line:
				info_update('Domain info: YMax = ' + line.split('(')[1].split(')')[0])
			elif 'problem.setXMin' in line:
				info_update('Domain info: XMin = ' + line.split('(')[1].split(')')[0])
			elif 'problem.setYMin' in line:
				info_update('Domain info: YMin = ' + line.split('(')[1].split(')')[0])
			
	# --------------------------------------------------------------------------- #

	# Copy c++ file and CMakeLists file to target directory

	if timestep_last == 1:		
		Dir_name = project_name											# Directory name is kept same as project name 
	else:
		Dir_name = project_name + '_' + str(timestep_last)				# Directory name is changed according to timestep
	
	try:			
		
		# If no errors occur, the directory is created.
							
		os.mkdir('/home/'+username+'/MercuryDPM/MercurySource/Drivers/'+Dir_name)		
		
		info_update('Created directory in MercuryDPM folder...')
		 
	except OSError:
		
		info_update('Directory already exists in MercuryDPM folder...')
		
		info_update('Removing contents...')
		
		# If a directory exists with the same name, the directory is removed from both the source and build folders and created afterwards. 
		
		shutil.rmtree('/home/'+username+'/MercuryDPM/MercurySource/Drivers/'+Dir_name)	
		shutil.rmtree('/home/'+username+'/MercuryDPM/MercuryBuild/Drivers/'+Dir_name)
		
		info_update('Contents removed...')
		
		os.mkdir('/home/'+username+'/MercuryDPM/MercurySource/Drivers/'+Dir_name)
		
		info_update('Created directory in MercuryDPM folder...')
		
	print '\nDirectory created..'
	print '\nCopying files..'
	shutil.copyfile(File, '/home/'+username+'/MercuryDPM/MercurySource/Drivers/'+Dir_name+ '/'+File_name)					# Copy the cpp file with the simulation parameters in the source folder. 
	shutil.copyfile(cmakefile, '/home/'+username+'/MercuryDPM/MercurySource/Drivers/'+Dir_name+ '/' + 'CMakeLists.txt')		# Copy CMakeLists file as well to the source folder. 
	print '\nDone..'
	
	info_update('Copied CMakeLists file and cpp file to Drivers/'+project_name+'...')
	
	# --------------------------------------------------------------------------- #
	
	# Create or modify the CMakeLists.txt file within MercurySource/Drivers and add the new target to be compiled. 
	# The new target corresponds to the user created cpp file with simulation parameters. 
	
	info_update('Modifying CMakeLists file to add target...')
	
	os.chdir('/home/'+username+'/MercuryDPM/MercurySource/Drivers')
	list_dir = os.listdir(os.getcwd())
	Required_dir = ['CMakeLists.txt', 'CMakeCache.txt', 'Makefile', 'CMakeFiles', 'cmake_install.cmake', 'Configuration','CTestTestfile.cmake']
	Cfile = open('CMakeLists.txt','w')
	Cfile.write('cmake_minimum_required (VERSION 2.8)\n\n')
	
	for i in list_dir:
		if not i in Required_dir:
				Cfile.write('add_subdirectory('+i+')\n')
	Cfile.close()
	remember = 1
	
	info_update('Target added in CMakeLists file...')
	
	# --------------------------------------------------------------------------- #

	# Compile c++ program and create the executable file in MercuryBuild
	
	info_update('Compiling c++ program...')

	print '\nCompiling program..'
	os.chdir('/home/'+username+'/MercuryDPM/MercurySource')
	#info_update('Running cmake in source folder...')
	os.system('cmake .')												# Run cmake in Source folder
	os.chdir('/home/'+username+'/MercuryDPM/MercuryBuild')
	#info_update('Running cmake in build folder...')
	os.system('cmake .')												# Run cmake in Build folder
	print '\nBuilding executable file..'
	info_update('Running make in project directory...')
	os.system('make '+File_name[:-4])									# make command compiles the target. 
	
	# --------------------------------------------------------------------------- #

	# Run the executable file

	print '\nRunning executable file..'
	
	if remember == 1:
		os.chdir('/home/'+username+'/MercuryDPM/MercuryBuild/Drivers/'+Dir_name)
		os.system(r'./'+File_name[:-4])
		info_update('Execution complete...')
	else:
		os.chdir('/home/'+username+'/MercuryDPM/MercuryBuild/Drivers/'+Dir.split('/')[-1])
		os.system(r'./'+File_name[:-4])
		info_update('Execution complete...')
		
	return timestep
	# --------------------------------------------------------------------------- #
