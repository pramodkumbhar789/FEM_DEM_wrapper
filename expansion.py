# Developed by 
# Pramod Kumbhar, Narasimhan Swaminathan, Ratna Kumar Annabattula
# Mesoscale analysis of Li-ion battery microstructure using sequential coupling of discrete element and finite element method.
# International Journal of Energy Research.


################################ Purpose #########################################
# To compute the expansion 
##################################################################################


from sys import path
import numpy as np
import odbAccess
from textRepr import *
from string import *
from time import *
import os
import sys
import pprint

def lagrange_basis(xi,eta,nnode):
	
	if nnode == 3:
		N=[1-xi-eta,xi,eta];
		dNdxi=[[-1,-1],[1,0],[0,1]];
	elif nnode == 6:	
		N=[1-3*(xi+eta)+4*xi*eta+2*(xi**2+eta**2), \
							  xi*(2*xi-1), \
							  eta*(2*eta-1), \
							  4*xi*(1-xi-eta), \
							  4*xi*eta, \
							  4*eta*(1-xi-eta)
							  ];
		
		dNdxi=[[-3+4*eta+4*xi ,-3+4*xi+4*eta], \
			  [4*xi-1,0.0], \
			  [0,4*eta-1], \
			  [4*(1-eta-2*xi),-4*xi], \
			  [4*eta,4*xi], \
			  [-4*eta,4*(1-xi-eta)-4*eta]]
	
	return N,dNdxi
		  
def quadrature(ngp):
	
	
		
	quadpoint=[[],[]]
	quadweight=[]
		
	if ngp == 1:
		quadpoint[0].append(0.333333333333300)
		quadpoint[1].append(0.333333333333300)
		quadweight.append(0.500000000000000)
	elif ngp==3:
		quadpoint[0].append(0.166666666666700)
		quadpoint[1].append(0.166666666666700)
		quadpoint[0].append(0.666666666666700)
		quadpoint[1].append(0.166666666666700)
		quadpoint[0].append(0.166666666666700)
		quadpoint[1].append(0.666666666666700)
	
		quadweight.append(0.166666666666650)
		quadweight.append(0.166666666666650)
		quadweight.append(0.166666666666650)
	elif ngp==7:
		quadpoint[0].append(0.101286507323500)
		quadpoint[1].append(0.101286507323500)
		quadpoint[0].append(0.797426985353100)
		quadpoint[1].append(0.101286507323500)
		quadpoint[0].append(0.101286507323500)
		quadpoint[1].append(0.797426985353100)
		quadpoint[0].append(0.470142064105100)
		quadpoint[1].append(0.059715871789800)
		quadpoint[0].append(0.470142064105100)
		quadpoint[1].append(0.470142064105100)
		quadpoint[0].append(0.059715871789800)
		quadpoint[1].append(0.470142064105100)
		quadpoint[0].append(0.333333333333300)
		quadpoint[1].append(0.333333333333300)
		
        
		quadweight.append(0.062969590272400)
		quadweight.append(0.062969590272400)
		quadweight.append(0.062969590272400)
		quadweight.append(0.066197076394250)
		quadweight.append(0.066197076394250)
		quadweight.append(0.066197076394250)
		quadweight.append(0.112500000000000) 
	elif ngp==13:
		quadpoint[0].append(0.065130102902200)
		quadpoint[1].append(0.065130102902200)
		quadpoint[0].append(0.869739794195600)
		quadpoint[1].append(0.065130102902200)
		quadpoint[0].append(0.065130102902200)
		quadpoint[1].append(0.869739794195600)
		quadpoint[0].append(0.312865496004900)
		quadpoint[1].append(0.048690315425300)
		quadpoint[0].append(0.638444188569800)
		quadpoint[1].append(0.312865496004900)
		quadpoint[0].append(0.048690315425300)
		quadpoint[1].append(0.638444188569800)
		quadpoint[0].append(0.638444188569800)
		quadpoint[1].append(0.048690315425300)
		quadpoint[0].append(0.312865496004900)
		quadpoint[1].append(0.638444188569800)
		quadpoint[0].append(0.048690315425300)
		quadpoint[1].append(0.312865496004900)
		quadpoint[0].append(0.260345966079000)
		quadpoint[1].append(0.260345966079000)
		quadpoint[0].append(0.479308067841900)
		quadpoint[1].append(0.260345966079000)
		quadpoint[0].append(0.260345966079000)
		quadpoint[1].append(0.479308067841900)
		quadpoint[0].append(0.333333333333300)
		quadpoint[1].append(0.333333333333300)

		quadweight.append(0.026673617804400)
		quadweight.append(0.026673617804400)
		quadweight.append(0.026673617804400)
		quadweight.append(0.038556880445150)
		quadweight.append(0.038556880445150)
		quadweight.append(0.038556880445150)
		quadweight.append(0.038556880445150)
		quadweight.append(0.038556880445150)
		quadweight.append(0.038556880445150)
		quadweight.append(0.087807628816600)
		quadweight.append(0.087807628816600)
		quadweight.append(0.087807628816600)
		quadweight.append(-0.074785022233850)
		
	Q=quadpoint
	W=np.float64(quadweight)
	return W,Q

def quadrature_node(ngp):
	
		
	quadpoint=[[],[]]
	quadweight=[]

	quadpoint[0].append(0.00)
	quadpoint[1].append(0.00)
	quadpoint[0].append(1.00)
	quadpoint[1].append(0.00)
	quadpoint[0].append(0.00)
	quadpoint[1].append(1.00)

	quadweight.append(0.166666666666650)
	quadweight.append(0.166666666666650)
	quadweight.append(0.166666666666650)
	
	Q=quadpoint
	W=np.float64(quadweight)	
	return W,Q

	
def getMatMtx(E,nu,string):
	if string =='plane_strain':
		D_mat=np.array([[E*(1-nu)/((1+nu)*(1-2*nu)),E*nu/((1+nu)*(1-2*nu)),0],[E*nu/((1+nu)*(1-2*nu)),E*(1-nu)/((1+nu)*(1-2*nu)),0],[0,0,E*(1-2*nu)/(2*(1+nu)*(1-2*nu))]])
	elif string =='plane_stress':
		D_mat=E/(1-nu**2)*np.array([[1,nu,0],[nu,1,0],[0,0,(1-nu)/2]])
	return D_mat
def exp_exec():
	# Material Props
	E=19.25e9 # Young's modulus
	nu=0.3 # Poisson's ratio
	omega=4.17e-6  # partial molar volume (3*alpha in thermo-elasticity)
	cmax=30555  # changed before the presentation on 18 Sep, 2018 in Narasimhan sir's group
	R=8.314 # universal gas constant
	T=300  #temp
	E_nd=omega*E/R/T  # non-dimensional E
	ome_nd=omega*cmax   # non-dimensional omega
	Coeff=E_nd*ome_nd/3/(1-2*nu)   # for thermal stresses plane strain # 1-2*nu for plane_strain; 1-nu for plane_stress
	D=getMatMtx(E_nd,nu,'plane_strain')   # non-dimensionalized D-material matrix

	ngp=7 # for volume expansion
	ngp_stress=3 # for calculation of stresses
	Temp = []
	u = []
	cwd = os.getcwd()
	name=['Job__24s']
	for ni in name:
		Name=cwd+'/'+ni+'.odb'
		myOdb = odbAccess.openOdb(path=Name)
		stepnames=myOdb.steps
		for ki in range(len(stepnames.keys())):
			nameOfStep= stepnames.keys()[ki]
		assembly=myOdb.rootAssembly
		instance=assembly.instances
		allinstance=str(instance)
		autoins=allinstance.split("'")
		inslen=len(autoins)/4
		instancename=autoins[inslen]
		numnode=len(instance[instancename].nodes)
		numelem=len(instance[instancename].elements)
		W,Q = quadrature_node(ngp_stress)
		# At gauss points
		strain_gp = [[[0 for k in xrange(3)] for j in xrange(np.shape(W)[0])] for i in xrange(numelem)] # epsilon_11,epsilon_22,epsilon_12 for # gauss points
		ther_strain_gp=([[[0 for k in xrange(3)] for j in xrange(np.shape(W)[0])] for i in xrange(numelem)]) # eps_ther_11,eps_ther_22,eps_ther_12
		stress_gp=([[[0 for k in xrange(3)] for j in xrange(np.shape(W)[0])] for i in xrange(numelem)]) # str_11,str_22,str_12
		szz_gp=	([[[0 for k in xrange(1)] for j in xrange(np.shape(W)[0])] for i in xrange(numelem)]) # str_33
		sh_gp=	([[[0 for k in xrange(1)] for j in xrange(np.shape(W)[0])] for i in xrange(numelem)]) # str_h
		nodes=instance[instancename].nodes
		lastStep=myOdb.steps[nameOfStep]	
		z=	len(lastStep.frames)-1	
		lastFrame = myOdb.steps[nameOfStep].frames[z]
		currFrame = myOdb.steps[nameOfStep].frames[z]
		Times=currFrame.frameValue
		deformation=lastFrame.fieldOutputs['U']
		tempObj=lastFrame.fieldOutputs['NT11']
		for i in range(len(currFrame.fieldOutputs['NT11'].values)):
			Temp.append(currFrame.fieldOutputs['NT11'].values[i].data)
			u.append(deformation.values[i].data)

	myOdb = odbAccess.openOdb(path=Name)
	assembly=myOdb.rootAssembly
	instance=assembly.instances
	allinstance=str(instance)
	autoins=allinstance.split("'")
	inslen=len(autoins)/4
	instancename=autoins[inslen]
	numnode=len(instance[instancename].nodes)
	numelem=len(instance[instancename].elements)
	nodes=instance[instancename].nodes

	element_file = 'Element24.txt'

	with open(element_file) as file:
		data = file.read()
		
	data = data.split('\n')

	element_list = []

	for i in range(len(data)-1):
		element_list.append(map(int,data[i].split(',')[1:]))
		
	coord_all = []
	centroidx_all = []
	centroidy_all = []

	element=element_list

	for i in range(len(element)):
		econ=np.subtract(element[i],1)
		ncoord=[]
		disp=[]
		temp=[]
		for j in range(len(econ)):
			ncoord.append([nodes[econ[j]].coordinates[0],nodes[econ[j]].coordinates[1]])
			disp.append(deformation.values[econ[j]].data)
			temp.append(tempObj.values[econ[j]].data)
		nnode=np.shape(ncoord)[0]
		disp=np.array(disp)
		temp=np.array(temp)	
		for igp in range(len(W)):
			pt = [Q[0][igp],Q[1][igp]]
			N,dNdxi=lagrange_basis(pt[0],pt[1],nnode)
			Jo = np.dot(np.transpose(dNdxi), ncoord)
			Gpt = np.dot(np.transpose(N),ncoord)
			J = np.linalg.inv(Jo)
			dNdx = np.dot(J,np.transpose(dNdxi))
			dNdx=np.array(dNdx)	
			strain_gp[i][igp][0]=np.dot(dNdx[0,:],np.array(disp)[:,0])		
			strain_gp[i][igp][1]=np.dot(dNdx[1,:],np.array(disp)[:,1])		
			strain_gp[i][igp][2]=np.dot(dNdx[0,:],np.array(disp)[:,1])+np.dot(dNdx[1,:],np.array(disp)[:,0])
			temp_gp=np.dot(N,np.array(temp)[:])
			ther_strain_gp[i][igp][0]=ome_nd/3*np.dot(N,np.array(temp)[:]) # change multiplication factor later
			ther_strain_gp[i][igp][1]=ome_nd/3*np.dot(N,np.array(temp)[:])
			ther_strain_gp[i][igp][2]=0.0
			stress_gp[i][igp][0:]=np.dot(D,strain_gp[i][igp][:])-Coeff*np.array([temp_gp,temp_gp,0.0])
			szz_gp[i][igp][0]=nu*(stress_gp[i][igp][0]+stress_gp[i][igp][1])-E_nd*ome_nd/3*np.dot(N,np.array(temp)[:])
			sh_gp[i][igp][0]=(stress_gp[i][igp][0]+stress_gp[i][igp][1]+szz_gp[i][igp][0])/3.0
	# At nodes
	element=np.array(element)
	vertex=element[:,0:3] # extract vertices of all the elements
	num_vertex=np.shape(np.unique(vertex))[0] # get number of vertices

	# initialize the matrix for strain and stress at nodes # done by interelement averaging
	avg_strain_node=[[0 for k in xrange(3)] for j in xrange(num_vertex)] # epsilon_11,epsilon_22,epsilon_12 for # nodes 3 for triangular
	avg_stress_node=[[0 for k in xrange(3)] for j in xrange(num_vertex)] # stress_11,stress_22,stress_12 for # nodes 3 for triangular
	avg_szz_node=[[0 for k in xrange(1)] for j in xrange(num_vertex)] # stress_33 for # nodes 3 for triangular
	avg_sh_node=[[0 for k in xrange(1)] for j in xrange(num_vertex)] # stress_h for # nodes 3 for triangular

	# convert into arrays
	strain_gp=np.array(strain_gp)
	ther_strain_gp=np.array(ther_strain_gp)
	stress_gp=np.array(stress_gp)
	szz_gp=np.array(szz_gp)
	sh_gp=np.array(sh_gp)
	vertex_list, inverse = np.unique(vertex, return_inverse = True)
	for i in range(num_vertex):
		curr_node=vertex_list[i]
		ind=zip(*np.where(element[:,0:3] == curr_node)) # search for node i in first 3 columns viz., 0,1,2 # 3 is excluded 
		for j in range(np.shape(ind)[0]):
			avg_strain_node[i][0] = avg_strain_node[i][0]+strain_gp[ind[j][0]][ind[j][1]][0]		# for epsilon_11 
			avg_strain_node[i][1] = avg_strain_node[i][1]+strain_gp[ind[j][0]][ind[j][1]][1]		# for epsilon_22
			avg_strain_node[i][2] = avg_strain_node[i][2]+strain_gp[ind[j][0]][ind[j][1]][2]		# for epsilon_12
			avg_stress_node[i][0] = avg_stress_node[i][0]+stress_gp[ind[j][0]][ind[j][1]][0]		# for stress_11
			avg_stress_node[i][1] = avg_stress_node[i][1]+stress_gp[ind[j][0]][ind[j][1]][1]		# for stress_22   
			avg_stress_node[i][2] = avg_stress_node[i][2]+stress_gp[ind[j][0]][ind[j][1]][2]		# for stress_12   
			avg_szz_node[i][0]    = avg_szz_node[i][0]   +szz_gp[ind[j][0]][ind[j][1]][0]
			avg_sh_node[i][0]     = avg_sh_node[i][0]    +sh_gp[ind[j][0]][ind[j][1]][0]
		avg_strain_node[i][:]=np.array(avg_strain_node[i][:])/np.shape(ind)[0]
		avg_stress_node[i][:]=np.array(avg_stress_node[i][:])/np.shape(ind)[0]
		avg_szz_node[i][:]=np.array(avg_szz_node[i][:])/np.shape(ind)[0]
		avg_sh_node[i][:]=np.array(avg_sh_node[i][:])/np.shape(ind)[0]
	avg_strain_node=np.array(avg_strain_node)
	avg_stress_node=np.array(avg_stress_node)
	avg_szz_node=np.array(avg_szz_node)
	avg_sh_node=np.array(avg_sh_node)

	S11 = avg_stress_node[:,0]
	S22 = avg_stress_node[:,1]
	S12 = avg_stress_node[:,2]
	S33 = avg_szz_node[:,0]
	SH  = avg_sh_node[:,0]

	E11 = avg_strain_node[:,0]
	E22 = avg_strain_node[:,1]
	E12 = avg_strain_node[:,2]

	S11_build = np.reshape(S11[inverse], (len(vertex), 3))
	S22_build = np.reshape(S22[inverse], (len(vertex), 3))
	S12_build = np.reshape(S12[inverse], (len(vertex), 3))
	S33_build = np.reshape(S33[inverse], (len(vertex), 3))
	SH_build = np.reshape(SH[inverse], (len(vertex), 3))

	E11_build = np.reshape(E11[inverse], (len(vertex), 3))
	E22_build = np.reshape(E22[inverse], (len(vertex), 3))
	E12_build = np.reshape(E12[inverse], (len(vertex), 3))

	S11_complete = []
	S22_complete = []
	S12_complete = []
	S33_complete = []
	SH_complete = []
	E11_complete = []
	E22_complete = []
	E12_complete = []

	for i in range(len(S11_build)):
		S11_complete.append(np.append(S11_build[i], [0,0,0]))
		S22_complete.append(np.append(S22_build[i], [0,0,0]))
		S12_complete.append(np.append(S12_build[i], [0,0,0]))
		S33_complete.append(np.append(S33_build[i], [0,0,0]))
		SH_complete.append(np.append(SH_build[i], [0,0,0]))
		E11_complete.append(np.append(E11_build[i], [0,0,0]))
		E22_complete.append(np.append(E22_build[i], [0,0,0]))
		E12_complete.append(np.append(E12_build[i], [0,0,0]))
		
	S11_complete_flatten = np.array([item for sublist in S11_complete for item in sublist])
	S22_complete_flatten = np.array([item for sublist in S22_complete for item in sublist])
	S12_complete_flatten = np.array([item for sublist in S12_complete for item in sublist])
	S33_complete_flatten = np.array([item for sublist in S33_complete for item in sublist])
	SH_complete_flatten = np.array([item for sublist in SH_complete for item in sublist])
	E11_complete_flatten = np.array([item for sublist in E11_complete for item in sublist])
	E22_complete_flatten = np.array([item for sublist in E22_complete for item in sublist])
	E12_complete_flatten = np.array([item for sublist in E12_complete for item in sublist])
		
	element_unique, element_index = np.unique(element, return_index = True)

	S11_complete_unique = S11_complete_flatten[element_index]
	S22_complete_unique = S22_complete_flatten[element_index]
	S12_complete_unique = S12_complete_flatten[element_index]
	S33_complete_unique = S33_complete_flatten[element_index]
	SH_complete_unique = SH_complete_flatten[element_index]
	E11_complete_unique = E11_complete_flatten[element_index]
	E22_complete_unique = E22_complete_flatten[element_index]
	E12_complete_unique = E12_complete_flatten[element_index]

	stress_val_all = [[S11_complete_unique[i], S22_complete_unique[i], S12_complete_unique[i], S33_complete_unique[i], SH_complete_unique[i]] for i in range(len(S11_complete_unique))]
	strain_val_all = [[E11_complete_unique[i], E22_complete_unique[i], E12_complete_unique[i]] for i in range(len(E11_complete_unique))]

	for i in range(len(element)):
		econ=np.subtract(element[i],1)
		coord_new = []
		for j in range(len(econ)):
			coord_new.append([nodes[econ[j]].coordinates[0],nodes[econ[j]].coordinates[1]])
		coord_all.append(coord_new)
		centroidx_all.append((coord_all[i][0][0] + coord_all[i][1][0] + coord_all[i][2][0])/3)
		centroidy_all.append((coord_all[i][0][1] + coord_all[i][1][1] + coord_all[i][2][1])/3)
		
	with open('../../Particles.txt') as file:
		center_data = file.read()
		
	center_data = center_data.split('\n')

	xc = []
	yc = []
	rad = []
	for i in range(len(center_data)-1):
		temp = filter(None, center_data[i].split(' '))
		xc.append(np.float64(temp[0]))
		yc.append(np.float64(temp[1]))
		rad.append(np.float64(temp[2]) - np.float64(temp[0]))
		
	def compare(x1, y1, x2, y2, r1, r2):
		distsq = np.sqrt((x1-x2)**2 + (y1-y2)**2)
		radsum = r1+r2
		
		if distsq < radsum:
			return -1

	required_element_list = []
	for i in range(len(xc)):
		initial_list = []
		for j in range(len(centroidx_all)):
			if compare(centroidx_all[j],centroidy_all[j],xc[i],yc[i],rad[i]*1.01, 0) == -1:
				initial_list.append(j)
		required_element_list.append(initial_list)
		
	fvolume = open('volume_data.txt', 'a')
	element = np.array(element)
	W,Q = quadrature(ngp)
	z=	len(lastStep.frames)-1
	currFrame = myOdb.steps[nameOfStep].frames[z]
	deformation=currFrame.fieldOutputs['U']
		
	for k in range(1):
		
		element2 = element
				
		vol_final=0.0

		for i in range(len(element2)):
			econ=np.subtract(element2[i],1)
			ncoord=[]
			for j in range(len(econ)):
				ncoord.append([nodes[econ[j]].coordinates[0]+deformation.values[econ[j]].data[0],nodes[econ[j]].coordinates[1]+deformation.values[econ[j]].data[1]])


			for igp in range(len(W)):
				pt = [Q[0][igp],Q[1][igp]]
				N,dNdxi=lagrange_basis(pt[0],pt[1],np.shape(ncoord)[0])
				Jo = np.dot(np.transpose(dNdxi), ncoord)
				vol_final=vol_final+np.linalg.det(Jo)*W[igp]

	rad2 = [r**2 for r in rad] # Squaring each entry
	rad2sum = sum(rad2) 
	for k in range(len(rad)):
		fvolume.write(str(vol_final*rad2[k]/rad2sum)) # Assigning the area proportional to the square of the radii
		fvolume.write(',')
		fvolume.write(str(vol_final*rad2[k]/rad2sum)) # Assigning the area proportional to the square of the radii
		fvolume.write('\n')
	fvolume.write('**\n'); fvolume.close()

	file_open = open('Temp24.txt', 'w+')

	for i in Temp:
		file_open.write(str(i))
		file_open.write('\n')
		
	file_open1 = open('disp24.txt', 'w+')

	for j in u:
		file_open1.write(str(j))
		file_open1.write('\n')

	file_open2 = open('stress24.txt', 'w+')

	for i in stress_val_all:
		file_open2.write(str(i))
		file_open2.write('\n')

	file_open3 = open('strain24.txt', 'w+')

	for i in strain_val_all:
		file_open3.write(str(i))
		file_open3.write('\n')
		   
	file_open.close()
	file_open1.close()
	file_open2.close()
	file_open3.close()
		
	myOdb.close()	
exp_exec()
