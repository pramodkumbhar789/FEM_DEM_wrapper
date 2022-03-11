# Developed by  
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.


################################ Purpose #########################################
# Automation of the script generation file for DEM using MercuryDPM
##################################################################################


from __future__ import division
def group2MDPM(username,wrapper_path, info_file,ABAQUS_path,project_name,project_path,MDPM_path,timestep):
	
	# Import modules
	
	import os
	import numpy as np
	from time import strftime
	
	#global username,wrapper_path, info_file, ABAQUS_path,project_name,project_path,timestep 

	set_cpp_name = project_name			
	
	timestep_last = timestep					# Timestep information
	
	Info_file = open(info_file, 'a')					# Write log data to file
	
	# Obtain a list of all files in directory
	
	files_list = os.listdir(os.getcwd())				# Get list of all files in the folder
	
	# Sort the files list to avoid wrong numbering
	
	sort_counter = 0													# This ensures that the numbering is ascending
	
	sorted_files_list = []
	
	number_of_particles = []
	
	for i in files_list:
		if 'Group' in i:
			sorted_files_list.append('Group'+str(sort_counter)+'.txt')
			sort_counter += 1
	for i in files_list:
		if 'Particle' in i:
			sorted_files_list.append(i)
			
	# Read volume data after UEL expansion
	
	with open('ABAQUS/RESULTS/volume_data.txt') as file:
		vol_data = file.read()
		
	vol_data = vol_data.split('\n')
	
	vol_data_all = []
	
	for i in range(len(vol_data)-1):
		if '**' in vol_data[i]:
			pass
		else:
			vol_data_all.append(np.float64(vol_data[i].split(',')[1]))
			
	# Consolidate all data from the Grouped files
			
	x = []
	y = []
	radius = []
	particle_counter = 0
		
	for i in range(len(sorted_files_list)):
		with open(sorted_files_list[i]) as file:
			if i == len(sorted_files_list)-1:
				for line in file:
					temp = filter(None, line.split(' '))
					x.append(np.float64(temp[0]))
					y.append(np.float64(temp[1]))
					radius.append(np.sqrt((vol_data_all[particle_counter])/np.pi))
					particle_counter += 1
			else:
				for line in file:
					temp = filter(None, line.split(' '))
					x.append(np.float64(temp[0]))
					y.append(np.float64(temp[1]))
					radius.append(np.sqrt((vol_data_all[particle_counter])/np.pi))
					particle_counter += 1
					
	# Sort all information according to particle database
	
	with open(project_path+'/log/Particle_database'+ str(timestep_last) +'.txt') as file:
	#with open(project_path+'/log/Particle_database1.txt') as file:
		database_data = file.read()
		
	database_data = database_data.split('\n')
	
	id_info = []
	x_info = []
	y_info = []
	group_info = []
	
	for i in range(1,len(database_data)-1):
		p = filter(None, database_data[i].split(' '))
		id_info.append(p[0])
		x_info.append(p[1])
		y_info.append(p[2])
		group_info.append(p[4])
		
	x1 = [str(i) for i in x]
	
	reorder = []
	
	for i in x_info:
		for j, value in enumerate(x1):
			if i == value:
				reorder.append(j)
		
	x = [x[i] for i in reorder]
	y = [y[i] for i in reorder]
	radius = [radius[i] for i in reorder]
	
	# New timestep
	
	timestep_new = int(timestep_last) + 1
	
	Info_file.write('\n\n## ' + str(timestep_new) + '\n\n')	
	
	f = open('/home/'+username+'/MercuryDPM/MercuryBuild/Drivers/'+set_cpp_name+'_'+str(timestep_new)+ '.cpp', 'w+')
	
	Info_file.write('\n\n!! /'+ '/home/'+username+'/MercuryDPM/MercuryBuild/Drivers/' + set_cpp_name+'_'+str(timestep_new)+ '.cpp\n\n')	
	
	Info_file.write(strftime('[%H:%M:%S]'+'\t\tCreating new MDPM script...\n'))

	f.write(' #include <Species/LinearViscoelasticFrictionSpecies.h> \n\
	 #include <Mercury3D.h> \n\
	 #include <Particles/BaseParticle.h> \n\
	 #include <Walls/InfiniteWall.h> \n\n')





	f.write('class '+set_cpp_name+': public Mercury3D { \n \
		public:\n \
		void setupInitialConditions() {\n \
			species = new LinearViscoelasticFrictionSpecies();\n \
			speciesHandler.addObject(species);\n \
			species->setDensity(2.7e-6);\n \
			species->setStiffness(4.4596e-9);\n \
			species->setDissipation(6.5191e-10);\n \
			species->setSlidingStiffness(5.5089e-9);\n \
			species->setSlidingDissipation(5.9160e-10);\n \
			species->setSlidingFrictionCoefficient(0.15);\n \
			species->setSlidingFrictionCoefficientStatic(0.25);\n \
			//species->setDissipation(1.68e-9);\n\n')

	f.write('	BaseParticle p0;\n');fact=1e-3; # factor earlier was 1e-6; now edited by Pramod

	for i in range(len(x)):
		f.write('	particles['+str(i)+'] = particleHandler.copyAndAddObject(p0);\n \
		particles['+str(i)+']->setVelocity(Vec3D(0.0, 0.0, 0.0));\n \
		particles['+str(i)+']->setRadius('+str(radius[i]*fact)+');\n \
		particles['+str(i)+']->setPosition(Vec3D('+str(x[i]*fact)+','+str(y[i]*fact)+',0));\n \
		\n\n')

	#f.write(' PeriodicBoundary w0;\n \
		#xwall = boundaryHandler.copyAndAddObject(w0); \n \
		#xwall->set(Vec3D(1.0,0.0,0.0),getXMin(), getXMax());\n \
		#ywall = boundaryHandler.copyAndAddObject(w0);\n \
		#ywall->set(Vec3D(0.0,1.0,0.0),getXMin(), getXMax());\n \
	  #}\n\n')
	
	
	f.write('InfiniteWall w0;\n\
rightwall = wallHandler.copyAndAddObject(w0);					// Bottom wall\n\
rightwall->set(Vec3D(1.0,0.0,0.0),Vec3D(getXMax(), 0,0));		\n\
\n\
topwall = wallHandler.copyAndAddObject(w0);						// Top wall\n\
topwall->set(Vec3D(0.0,1.0,0.0),Vec3D(0, getYMax(),0));	\n\
\n\
leftwall = wallHandler.copyAndAddObject(w0);					// Left wall\n\
leftwall->set(Vec3D(-1.0,0.0,0.0),Vec3D(getXMin(),0,0));	\n\
\n\
bottomwall = wallHandler.copyAndAddObject(w0);					// Right wall\n\
bottomwall->set(Vec3D(0.0,-1.0,0.0),Vec3D(0,getYMin(),0));}\n\n')






	f.write('void actionsBeforeTimeStep () {\n\
	EnergyVal = getKineticEnergy();\n\
	if (count == 1){\n\
		maxval = EnergyVal;\n\
		}\n\
	if (EnergyVal > maxval) {\n\
		maxval = EnergyVal;\n\
		}\n\
	count += 1;\n\
	if (count % 1000 == 0) {\n\
        double p_fac=0.0; \n\
        for (int i = 0; i <'+str(len(x))+'; i++){\n\
        p_fac = p_fac + 3.1428*particles[i]->getRadius()*particles[i]->getRadius()/(0.161*0.161);} \n\
        std::cout << "p_fac: " << p_fac << std::endl; \n\
	std::cout << "Max: " << EnergyVal/maxval << std::endl;}\n\
	if ((EnergyVal/maxval) < 0.05) {\n\
		exit(0);\n\
		}\n\
	if (maxval == 0 && count > 1000){\n\
		exit(0);\n\
		}\n\
	};\n')
	
	f.write('public:\n \
		//PeriodicBoundary* xwall;\n \
		//PeriodicBoundary* ywall;\n \
		InfiniteWall* rightwall;\n \
		InfiniteWall* topwall;\n \
		InfiniteWall* leftwall;\n \
		InfiniteWall* bottomwall;\n \
		BaseParticle* particles['+str(len(x)-1)+'];\n \
		LinearViscoelasticFrictionSpecies* species;\n \
		double PF;\n\
		double particlecount;\n\
		int PFcounter = 1;\n\
		double factor = 0.0001;\n\
		int count = 1;\n\
		double EnergyVal;\n\
		double maxval;\n\
	};\n\n')

	f.write('int main(int argc, char *argv[])\n \
	{\n \
	  '+set_cpp_name+' problem; \n \
	  problem.setName("'+set_cpp_name+ '_' + str(timestep_new)+'");\n \
	  problem.setSystemDimensions(2);\n \
	  problem.setParticleDimensions(2);\n \
	  problem.setGravity(Vec3D(0,0,0));\n \
	  problem.setXMax(0.161);\n \
	  problem.setYMax(0.161);\n \
	  problem.setZMax(0.0);\n \
	  problem.setXMin(0);\n \
	  problem.setYMin(0);\n \
	  problem.setZMin(0);\n \
	  problem.setTimeMax(1000000e-6);\n \
	  \n \
	  //auto species0 = problem.speciesHandler.copyAndAddObject(HertzianViscoelasticSpecies());\n \
	  \n \
	  problem.setSaveCount(10);\n \
	  problem.dataFile.setFileType(FileType::ONE_FILE);\n \
	  problem.restartFile.setFileType(FileType::ONE_FILE);\n \
	  problem.fStatFile.setFileType(FileType::ONE_FILE);\n \
	  problem.eneFile.setFileType(FileType::NO_FILE);\n \
	  \n \
	  problem.setXBallsAdditionalArguments("-v0 -w0 -cmode 5");\n \
	  \n \
	  problem.setTimeStep(1e-5);\n \
	  problem.solve(argc, argv);\n \
	  \n \
	  return 0;\n \
	}')

	f.close()
	
	Info_file.write(strftime('[%H:%M:%S]'+'\t\tNew script created...\n'))
	
	Info_file.close()

	return timestep
