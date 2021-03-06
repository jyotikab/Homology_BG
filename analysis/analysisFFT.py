import pickle
import numpy as np
import pylab as pl
import matplotlib as mpl
mpl.use('Agg')
#from mpl_toolkits.axes_grid1 import make_axes_locatable
import scipy.fftpack as spfft

import matplotlib.cm as cm
from pylab import *
# Since its a sparse matrix
import scipy.sparse.linalg as sp
import itertools
import scipy.cluster.hierarchy as sph
import os
from pylab import *
#import tree_anal
#import paramsearchGA_DopDep as psGA
import paramsearchGA_DopDep_nonlinear as psGA
import knownUnknownParams as p

from scipy.optimize import curve_fit

knownparams = p.params["known"]


terms = ["d1ta","d1ti","d2ta","d2ti","fsita","fsiti","tad2","tata","tati","tid2","tita","titi","stnta","stnti","tistn","tastn","jc1","jc2","jfsictx","jstnctx"]
#terms1 = ["D1","D2","FSI","TA","TI","STN","GPi","Ctx"]
terms1 = ["d1","d2","fsi","ta","ti","stn","gpi","ipctx"]



storage_home = os.getcwd()+"../PD" # Or healthy 

path1 = storage_home+'/scripts/' # Path to store the results
path2 = storage_home+'/Dist/' # Path to jdf files
path3 = storage_home+'/jdf/'
path5 = storage_home+'/output/' # Path for output 

AllAs = pickle.load(open(path5+"AllAs.pickle","r"))
AllBs = pickle.load(open(path5+"AllBs.pickle","r"))
def analFFT():

	randSamp = np.random.randint(0,len(AllAs),1000)
	fftSpec= dict()

	ipctx1 = dict()
	ipctx1["ip"] = np.zeros((1,1001))	
	dt = p.params["dt"]	
	fftSpec["samps"] = randSamp
	ampSpec = []
	fftfreq = np.fft.fftfreq(int(len(ipctx1["ip"][0])/dt))[:(int(len(ipctx1["ip"][0])/dt))/2] # Had to calculate on local machine, since this version of numpy (1.7.2) doesnt have np.fft.rfftfreq

	inds = np.where(fftfreq*1000*100<=400)[0]

	Flags = []
	Flags.append("TransFreq")
	for i,samp in enumerate(randSamp):
		#temp = np.zeros((8,len(freqs),len(fftfreq)/10+1))
		temp = np.zeros((8,len(inds)))
		A = AllAs[samp]
		B = AllBs[samp]
		Rates = psGA.calcRates(Flags,1.0,A,B,False,ipctx1,iptau=p.params["iptau"])
		for k,nuc in enumerate(terms1):
			ffttemp = np.fft.rfft(Rates[nuc]-np.mean(Rates[nuc]))

			#temp[k][:] = (np.abs(ffttemp)/np.max(np.abs(ffttemp)))[inds]
			temp[k][:] = np.abs(ffttemp)[inds]
		ampSpec.append(temp)
	fftSpec["ampSpec"] = ampSpec

	pickle.dump(fftSpec,open(path5+"fftSpec.pickle","w"))

