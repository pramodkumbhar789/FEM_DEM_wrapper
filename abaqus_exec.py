# Developed by 
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.


################################ Purpose #########################################
# Automation of the mesh generation using Abaqus for FEM
##################################################################################



from numpy import *
from abaqus import *
from abaqusConstants import *;import os,sys
import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import step
import interaction
import load
import mesh
import optimization
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior
from caeModules import *
from driverUtils import executeOnCaeStartup
from caeModules import *
from driverUtils import executeOnCaeStartup

def Macro1(assembled_name,mesh_size):

    elemType1 = mesh.ElemType(elemCode=CPE8T, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=CPE6MT, elemLibrary=STANDARD, 
        secondOrderAccuracy=OFF, hourglassControl=DEFAULT, 
        distortionControl=DEFAULT)
    p = mdb.models['Model-1'].parts[assembled_name]
    f = p.faces
    faces = f.getSequenceFromMask(mask=('[#ffffffff:47 #fffffff]', ), ) # [#ffffffff:45 #1f ] 1521 particles
    pickedRegions =(faces, )
    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
    p = mdb.models['Model-1'].parts[assembled_name]
    #f = p.faces
    pickedRegions = f.getSequenceFromMask(mask=('[#ffffffff:47 #fffffff]', ), )
    p.setMeshControls(regions=pickedRegions, elemShape=TRI, allowMapped=False)
    #p = mdb.models['Model-1'].parts[assembled_name]
    p.seedPart(size=mesh_size, deviationFactor=0.1, minSizeFactor=0.1)
    #p = mdb.models['Model-1'].parts[assembled_name]
    p.generateMesh()
# Control variables

def aba_exec(file_name,mesh_size,file_name_counter):

	#mesh_size = 0.529810864317
	job_name = 'Job_'+str(file_name_counter)
	#file_name = 'Group0.txt' 
	#if file_name == 'Particles.txt':
	with open(file_name) as file:datatxt = file.read();datatxt = datatxt.split('\n');	num_particles=len(datatxt)-1; # Edited by Pramod
	if num_particles == 1:
		os.system('cp Particles.txt Particles_temp.txt')
		os.system('''awk '{for(i=0;i<1;i++)print}' Particles.txt >> Particles.txt''') # Edited by Pramod
	freeze_num_particles = num_particles
	session.viewports['Viewport: 1'].partDisplay.geometryOptions.setValues(
		referenceRepresentation=ON);Mdb()
	with open(file_name) as file:datatxt = file.read();datatxt = datatxt.split('\n')
	num_particles=len(datatxt)-1;
	session.viewports['Viewport: 1'].setValues(displayedObject=None)
	ins_names=[]#Initiation of instance tuple
	with open(file_name) as file:
		datatxt = file.read()

	datatxt = datatxt.split('\n')
	print len(datatxt)-1
	for particle in range(len(datatxt)-1):
	#: A new model database has been created.
		temp = filter(None, datatxt[particle].split(' '))
		x1=float64(temp[0])
		y1=float64(temp[1])
		x2=float64(temp[2])
		y2=float64(temp[1])
		print (x1,y1,x2,y2,num_particles)
		pname='Part-%d'%(particle+1)
		s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
			sheetSize=200.0)
		g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
		s.setPrimaryObject(option=STANDALONE)
		s.CircleByCenterPerimeter(center=(x1, y1), point1=(x2, y2))
		p = mdb.models['Model-1'].Part(name=pname, dimensionality=TWO_D_PLANAR, 
			type=DEFORMABLE_BODY)
		p = mdb.models['Model-1'].parts[pname]
		p.BaseShell(sketch=s)
		s.unsetPrimaryObject()
		p = mdb.models['Model-1'].parts[pname]
		session.viewports['Viewport: 1'].setValues(displayedObject=p)
		del mdb.models['Model-1'].sketches['__profile__']
		a = mdb.models['Model-1'].rootAssembly
		session.viewports['Viewport: 1'].setValues(displayedObject=a)
		session.viewports['Viewport: 1'].assemblyDisplay.setValues(
			optimizationTasks=OFF, geometricRestrictions=OFF, stopConditions=OFF)
		a = mdb.models['Model-1'].rootAssembly
		a.DatumCsysByDefault(CARTESIAN)
		p = mdb.models['Model-1'].parts[pname]
		iname='Part-%d-1'%(particle+1)
		a.Instance(name=iname, part=p, dependent=OFF)
		ins_names.append(a.instances[iname]) #Creating instace tupe for union

	a = mdb.models['Model-1'].rootAssembly
	if len(datatxt)-1 == 1:
		assembled_name='Part-1'
	else:
		assembled_name='Part-%d'%(num_particles+1)
		a.InstanceFromBooleanMerge(name=assembled_name, instances=(ins_names), originalInstances=SUPPRESS, domain=GEOMETRY)
	Macro1(assembled_name,mesh_size)
	mdb.Job(name='Job_'+str(file_name_counter), model='Model-1', description='', type=ANALYSIS,
			atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
			memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
			explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
			modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
			scratch='', parallelizationMethodExplicit=DOMAIN, numDomains=1, 
			activateLoadBalancing=False, multiprocessingMode=DEFAULT, numCpus=1)
	mdb.jobs['Job_'+str(file_name_counter)].writeInput(consistencyChecking=OFF)
	print('#####Wrote the input file#####')
	mdb.saveAs('model_'+str(file_name_counter)+'.cae')
	if freeze_num_particles == 1:
		os.system('mv Particles_temp.txt Particles.txt')

file_mesh_size = 'mesh_sizes.txt';
with open(file_mesh_size) as file:
	data = file.read()

data = data.split('\n')
for i in range(len(data)-1):
#for i in range(1):
	aba_exec(data[i].split('\t')[0],float(data[i].split('\t')[1]),i)
