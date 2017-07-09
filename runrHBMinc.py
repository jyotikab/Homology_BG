import numpy as np
import pickle
import numpy as np
import pylab as pl
import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.fftpack as spfft

import matplotlib.cm as cm
from pylab import *
# Since its a sparse matrix
import scipy.sparse.linalg as sp
import itertools
import scipy.cluster.hierarchy as sph
import os
from pylab import *
from scipy.stats import ks_2samp


storage_home = '/home/j.bahuguna/homology/Mallet/wojc1jc2/slowNormParams/newParams'

path1 = storage_home+'/scripts/' # Path to store the results
path2 = storage_home+'/Dist/' # Path to jdf files
path3 = storage_home+'/jdf/'
path5 = storage_home+'/output/' # Path for output 
pathname = storage_home+'/output/'

ipNo1 = 5
PDFPD = pickle.load(open(pathname+"PDFeaturesnew_"+str(ipNo1)+".pickle","r"))
clusPD = pickle.load(open(pathname+"clustersPDMore"+str(ipNo1)+".pickle","r"))
labelPD = pickle.load(open(pathname+"LabeledClustersPD"+str(ipNo1)+".pickle","r"))


pathname1 = storage_home+'/strictHealthy/output/'
PDFH = pickle.load(open(pathname1+"PDFeaturesnew_"+str(ipNo1)+".pickle","r"))
clusH = pickle.load(open(pathname1+"clustersH"+str(ipNo1)+".pickle","r"))
labelH = pickle.load(open(pathname1+"LabeledClustersH"+str(ipNo1)+".pickle","r"))

labels=["RobustHealthy","AR","TDMild","TDSevere","RobustPathological","SevereAkinesia","RH<->TDMild","TDMild<->TDSevere","RH<->AR","AR<->SA","SA<->RP","InBetween" ]


# Only consider 4 of PD and 0 of H, since thats what histograms show in the HistParams.pdf in paper

clusPD4 = clusPD[4]
clusH0 = clusH[0]

# Now calculate K-S and generate one script per parameter 

KSPos = np.zeros((6,1)) # K-S statistic
KSNeg = np.zeros((14,1))

MeansClus1Neg = np.zeros((14,1)) # Means
MeansClus2Neg = np.zeros((14,1))
MeansClus1Pos =  np.zeros((6,1))
MeansClus2Pos =  np.zeros((6,1))
VarsClus1Neg = np.zeros((14,1)) # Means
VarsClus2Neg = np.zeros((14,1))
VarsClus1Pos =  np.zeros((6,1))
VarsClus2Pos =  np.zeros((6,1))


terms = ["d1ta","d1ti","d2ta","d2ti","fsita","fsiti","tad2","tata","tati","tid2","tita","titi","stnta","stnti","tistn","tastn","d1ctx","d2ctx","fsictx","stnctx"]
# And their respetive ids in the matrix
ids = [(0,3),(0,4),(1,3),(1,4),(2,3),(2,4),(3,1),(3,3),(3,4),(4,1),(4,3),(4,4),(5,3),(5,4),(4,5),(3,5),(0,7),(1,7),(2,7),(5,7)]
posbin = np.arange(0,19,1)*0.8
negbin = np.arange(-8,0.5,0.3)*0.8
AllAsPD = pickle.load(open(pathname+"AllAs5.pickle","r"))
AllBsPD = pickle.load(open(pathname+"AllBs5.pickle","r"))

AllAsH = pickle.load(open(pathname1+"AllAs5.pickle","r"))
AllBsH = pickle.load(open(pathname1+"AllBs5.pickle","r"))

# RobustPathological
cluster1 = []
# Robust Healthy
cluster2 = []

As = np.array(AllAsPD)[clusPD4]
Bs = np.array(AllBsPD)[clusPD4]
for A,B in zip(As,Bs):
	cluster1.append(np.hstack((A,B.T)))

As = np.array(AllAsH)[clusH0]
Bs = np.array(AllBsH)[clusH0]
for A,B in zip(As,Bs):
	cluster2.append(np.hstack((A,B.T)))


# Calculate K-S 
for i in xrange(len(terms)):
	if i < 14:
		temp1 = np.array(cluster1)[:,ids[i][0],ids[i][1]]
		temp2 = np.array(cluster2)[:,ids[i][0],ids[i][1]]
		MeansClus1Neg[i] = np.mean(temp1)
		MeansClus2Neg[i] = np.mean(temp2)
		VarsClus1Neg[i] = np.var(temp1)
		VarsClus2Neg[i] = np.var(temp2)

		a1,b1 = np.histogram(temp1,bins=negbin,normed=True)
		a2,b2 = np.histogram(temp2,bins=negbin,normed=True)

		# Use normed distribution to calculate KL divergence
		KSNeg[i][:] = ks_2samp(temp1,temp2)[0] # First value is K-S statistic and second is p-value
	else:
		temp1 = np.array(cluster1)[:,ids[i][0],ids[i][1]]
		temp2 = np.array(cluster2)[:,ids[i][0],ids[i][1]]
		MeansClus1Pos[i-14] = np.mean(temp1)
		MeansClus2Pos[i-14] = np.mean(temp2)
		VarsClus1Neg[i-14] = np.var(temp1)
		VarsClus2Neg[i-14] = np.var(temp2)
		a1,b1 = np.histogram(temp1,bins=posbin,normed=True)
		a2,b2 = np.histogram(temp2,bins=posbin,normed=True)

		KSPos[i-14][:] = ks_2samp(temp1,temp2)[0]

# Now start with the lowest value of K-S and keep changing until the samples start changing the clusters
# First keep strict criteria, the samples should remain Robustpathological and Robustly healthy
# Stack all KS together

KSAll = np.vstack((KSNeg,KSPos))
MeanAll1 = np.vstack((MeansClus1Neg,MeansClus1Pos))
MeanAll2 = np.vstack((MeansClus2Neg,MeansClus2Pos))
VarAll1 = np.vstack((VarsClus1Neg,VarsClus1Pos))
VarAll2 = np.vstack((VarsClus2Neg,VarsClus2Pos))


KSAllSorted =  np.sort(KSAll,0)
KSValInfo = dict()
KSValInfo["KSAll"] = KSAll
KSValInfo["MeanAll1"] = MeanAll1
KSValInfo["MeanAll2"] = MeanAll2
KSValInfo["VarAll1"] = VarAll1
KSValInfo["VarAll2"] = VarAll2

pickle.dump(KSValInfo,open(pathname+"KSValInfoInc.pickle","w"))

curr_ind = 0
for i in xrange(1,21):# Here i represents how many elements to replace by their means
	x = KSAllSorted[:i]

	# Calculate 
	params = dict()
	params["idPD"] = 4
	params["idH"] = 0
	params["clusPD"] = clusPD4
	params["clusH"] = clusH0
	#params["KSAll"] = KSAll
	params["KS-val"] = [ j[0] for j in x]
	#ind1 = [ np.where(KSAll==j)[0] for j in x  ]
	ind1 = []
	for j in x:
		t1 = np.where(KSAll==j)[0]
		if len(t1)>1:
			ind1.append([t1[curr_ind].tolist()])
			curr_ind+=1
		else:
			ind1.append(t1.tolist())
#	if len(ind1) > 1: # Tere are more than 1 terms which have the same K-S value, so take them one by one

#		ind1 = ind1[curr_ind]
#		curr_ind+=1 # we think what to do about this 
	params["MeanPD"] = [ MeanAll1[j][0][0] for j in ind1]
	params["MeanH"] = [ MeanAll2[j][0][0] for j in ind1]
	params["conn"] = [terms[j[0]] for j in ind1]
	params["VarPD"] = [VarAll1[j][0][0] for j in ind1]
	params["VarH"] = [VarAll2[j][0][0] for j in ind1]
	params["ind1"] = [j[0] for j in  ind1]

	sim_name ="replaceHistsByMeansInc"
	fh = open(path3 + '%s%d.py'%(sim_name,i),'w')
	fh.write('import sys\n')
	fh.write("sys.path.insert(0,'/home/j.bahuguna/homology/Mallet/wojc1jc2/slowNormParams/')\n")
	fh.write('import replaceHistsByMeansInc as rHBM\n')
	fh.write('rHBM.replace(%s)\n'%(params))
	fh.close()


	print sim_name

	fh = open(path3 + '%s.jdf'%(sim_name),'w')
	content = [
	'#!/bin/bash\n',
	#   '#PBS -t 0-%d\n'%(len(comb_pars)-1),
	#'#SBATCH -o /home/j.bahuguna/homology/vAModel/output/test_job_.out',
	'#SBATCH --output=/home/j.bahuguna/homology/Mallet/wojc1jc2/slowNormParams/output/rHBM_%s%d.out'%(sim_name,i),
	'#SBATCH --error=/home/j.bahuguna/homology/Mallet/wojc1jc2/slowNormParams/output/rHBM_%s%d.err'%(sim_name,i),
	#'#PBS -j oe\n',
	'#SBATCH --job-name=%s\n'%(sim_name),
	'#SBATCH --mem-per-cpu=3500mb\n',
	'#SBATCH --time 9:00:00\n',
	#'#SBATCH -p long \n',
	#'#SBATCH --output=%s%s_%s.txt\n'%(path3,sim_name,postfix),
	#'export PYTHONPATH=/clustersw/cns/nest-2.2.2/lib/python2.7/dist-packages/:$PYTHONPATH\n',
	'python /home/j.bahuguna/homology/Mallet/wojc1jc2/slowNormParams/jdf/%s%d.py\n'%(sim_name,i),
	#'python /bcfgrid/data/padmanabhan/scripts/levcomp/batch/%s_%s.py'%(sim_name,str(nr))
	]
	fh.writelines(content)
	fh.close()
	filename = path3 + '%s.jdf'%(sim_name)	
	os.system('sbatch  %s'%filename )

