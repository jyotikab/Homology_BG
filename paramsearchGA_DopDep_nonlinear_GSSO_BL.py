
import matplotlib as mpl
mpl.use('Agg')

import pylab as pl
import numpy as np
import matplotlib.cm as cm
from pylab import *
# Since its a sparse matrix
import scipy.sparse.linalg as sp
import itertools
import marshal
import pickle
# Plotting the nullclines, how they vary with lambda-CTX
import logging
import gc
import knownUnknownParams as p
from scipy.integrate import odeint
import funcs as fs
from checkPDFeaturesStrRed import *

def calc_GSSO(TransRates):
	PDFeatures = np.ones((1,8))
	dt = p.params["dt"]
	howmuch = (np.mean(TransRates['gpi'][100/dt:500/dt]) -np.mean(TransRates['gpi'][600/dt:1400/dt]))/np.mean(TransRates['gpi'][100/dt:500/dt])		# (Orig - Final)/Orig
	PDFeatures[0][0] = howmuch

	noiseLim = 0.5
	timeStart = 510
	timeStart2 = 520
	#timeEnd = 1480	
	timeEnd1 = 1000 # This took a lot of time to tune, so there is a tradeoff between frequency resolution and time resolution,if frequency resolution increases, longer length of signal, temporal resolution deecreases, which means the peak in spectrum becomes wider and shifts towards higher frequencies, ultimately slipping outside the beta band. If shorter length of signal is sent (time_range < len(TransRates)), temporal resolution increases peak becomes thinner or more precise but then again shifts towards lower frequencies. So a compromise reached at 1000. For damped oscillations the signal length also needed to be decreased.  	
	timeEnd2 = 650   	
	timeEnd3 = 900   	
	# An alternatiev idea to SE could be , percentage of power contained in beta-band (periodogram)- because you require some value fot susceptibility to oscillations which varies between 0 and 1
	noise = np.random.uniform(-noiseLim,noiseLim,len(TransRates['gpi'][timeStart/dt:timeEnd1/dt]))
	time = np.arange(0,len(noise),1)
	wind = np.exp(-time/10.)
	noise1 = np.convolve(noise,wind,mode='same')
	ind = np.where(noise1<0)
	noise1[ind] = 0.

	#TransRates['stn'][timeStart/dt:timeEnd/dt] += noise
	#TransRates['stn'][timeStart/dt:timeEnd1/dt] += noise1[:len(noise)]

	#se1,dfreq1 = spec_entropy(TransRates['stn'][timeStart/dt:timeEnd/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd/dt],freq_range=[0.015,0.025]) 
	se11,dfreq11,maxFreq11,perMax11 =   spec_entropy(TransRates['stn'][timeStart/dt:timeEnd1/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd1/dt],freq_range=[0.00009,0.00017]) # 0.00010 = 10 Hz, since resolution = 10^-5 sec, 1000msec, and dt = 0.01 , to better the resolution of frequency captured by fft
	se12,dfreq12,maxFreq12,perMax12 =   spec_entropy(TransRates['stn'][timeStart/dt:timeEnd2/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd2/dt],freq_range=[0.00007,0.00017]) # 0.00010 = 10 Hz, since resolution = 10^-5 sec, 1000msec, and dt = 0.01 , to better the resolution of frequency captured by fft
	se13,dfreq13,maxFreq13,perMax13 =   spec_entropy(TransRates['stn'][timeStart/dt:timeEnd1/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd1/dt],freq_range=[0.00017,0.00036]) # 0.00010 = 10 Hz, since resolution = 10^-5 sec, 1000msec, and dt = 0.01 , to better the resolution of frequency captured by fft
	se14,dfreq14,maxFreq14,perMax14 =   spec_entropy(TransRates['stn'][timeStart/dt:timeEnd2/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd2/dt],freq_range=[0.00017,0.00036]) # 0.00010 = 10 Hz, since resolution = 10^-5 sec, 1000msec, and dt = 0.01 , to better the resolution of frequency captured by fft
	se15,dfreq15,maxFreq15,perMax15 =   spec_entropy(TransRates['stn'][timeStart2/dt:timeEnd3/dt],time_range=TransRates["ipctx"][timeStart2/dt:timeEnd3/dt],freq_range=[0.00017,0.00036]) # 0.00010 = 10 Hz, since resolution = 10^-5 sec, 1000msec, and dt = 0.01 , to better the resolution of frequency captured by fft
	se16,dfreq16,maxFreq16,perMax16 = spec_entropy(TransRates['stn'][timeEnd1/dt:(timeEnd1+480.)/dt],time_range=TransRates["ipctx"][timeEnd1/dt:(timeEnd1+500.)/dt],freq_range=[0.0001,0.00025]) # 0.00010 = 10 Hz, since resolution = 10^-5 sec, 1000msec, and dt = 0.01 , to better the resolution of frequency captured by fft , If the oscillation occurs at the end of the stimulation period

	#se1,dfreq1,maxFreq1,perMax = spec_entropy(TransRates['stn'][timeStart/dt:timeEnd/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd/dt],freq_range=[0.00008,0.00020]) # 0.00010 = 10 Hz, since resolution = 10^-5 sec, 1000msec, and dt = 0.01 , to better the resolution of frequency captured by fft
	ans = np.array([se11,se12,se13,se14,se15,se16])
	indnan = np.where(np.isnan(ans)==True)
	ans[indnan] = 1
	print ans
	indmin = np.where(ans==np.min(ans))[0]
	print indmin
	#PDFeatures[i][2] = ans[indmin]
	PDFeatures[0][2] = np.min(ans)
	#PDFeatures[i][2] = np.mean(ans)
	#	if se11 < se12:
	#		PDFeatures[i][2] = se11 
			#maxFreq[i][0] = maxFreq11
			#perPowerMaxFreq[i][0] = perMax11
	#	else:
	#		PDFeatures[i][2] = se12 
			#maxFreq[i][0] = maxFreq12
			#perPowerMaxFreq[i][0] = perMax12
		
		#TransRates['ta'][timeStart/dt:timeEnd/dt] += noise
		#TransRates['ta'][timeStart/dt:timeEnd1/dt] += noise1[:len(noise)]

		#se2,dfreq2 = spec_entropy(TransRates['ta'][timeStart/dt:timeEnd/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd/dt],freq_range=[0.015,0.025])
	se21,dfreq21,maxFreq21,perMax21 =   spec_entropy(TransRates['ta'][timeStart/dt:timeEnd1/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd1/dt],freq_range=[0.00009,0.00017])
	se22,dfreq22,maxFreq22,perMax22 =   spec_entropy(TransRates['ta'][timeStart/dt:timeEnd2/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd2/dt],freq_range=[0.00007,0.00017])
	se23,dfreq23,maxFreq23,perMax23 =   spec_entropy(TransRates['ta'][timeStart/dt:timeEnd1/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd1/dt],freq_range=[0.00017,0.00036])
	se24,dfreq24,maxFreq24,perMax24 =   spec_entropy(TransRates['ta'][timeStart/dt:timeEnd2/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd2/dt],freq_range=[0.00017,0.00036])
	se25,dfreq25,maxFreq25,perMax25 =   spec_entropy(TransRates['ta'][timeStart2/dt:timeEnd3/dt],time_range=TransRates["ipctx"][timeStart2/dt:timeEnd3/dt],freq_range=[0.00017,0.00036])
	se26,dfreq26,maxFreq26,perMax26 = spec_entropy(TransRates['ta'][timeEnd1/dt:(timeEnd1+480.)/dt],time_range=TransRates["ipctx"][timeEnd1/dt:(timeEnd1+500.)/dt],freq_range=[0.0001,0.00025]) # 0.00010 = 10 Hz, since resolution = 10^-5 sec, 1000msec, and dt = 0.01 , to better the resolution of frequency captured by fft , If the oscillation occurs at the end of the stimulation period
	#se2,dfreq2,maxFreq1,perMax = spec_entropy(TransRates['ta'][timeStart/dt:timeEnd/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd/dt],freq_range=[0.00008,0.00020])
	ans = np.array([se21,se22,se23,se24,se25,se26])
	indnan = np.where(np.isnan(ans)==True)
	ans[indnan] = 1
	print ans
	indmin = np.where(ans==np.min(ans))[0]
	print indmin
	#PDFeatures[i][3] = ans[indmin]
	PDFeatures[0][3] = np.min(ans)
	#PDFeatures[i][3] = np.mean(ans)


	noise = np.random.uniform(-noiseLim,noiseLim,len(TransRates['ti'][timeStart/dt:timeEnd1/dt]))

	#TransRates['ti'][timeStart/dt:timeEnd/dt] += noise
	#TransRates['ti'][timeStart/dt:timeEnd1/dt] += noise1[:len(noise)] # At least for healthy, works better without colored noise

	#se3,dfreq3 = spec_entropy(TransRates['ti'][timeStart/dt:timeEnd/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd/dt],freq_range=[0.015,0.025])
	se31,dfreq31,maxFreq31,perMax31 =   spec_entropy(TransRates['ti'][timeStart/dt:timeEnd1/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd1/dt],freq_range=[0.00009,0.00017])
	se32,dfreq32,maxFreq32,perMax32 =   spec_entropy(TransRates['ti'][timeStart/dt:timeEnd2/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd2/dt],freq_range=[0.00007,0.00017])
	se33,dfreq33,maxFreq33,perMax33 =   spec_entropy(TransRates['ti'][timeStart/dt:timeEnd1/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd1/dt],freq_range=[0.00017,0.00036])
	se34,dfreq34,maxFreq34,perMax34 =   spec_entropy(TransRates['ti'][timeStart/dt:timeEnd2/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd2/dt],freq_range=[0.00017,0.00036])
	se35,dfreq35,maxFreq35,perMax35 =   spec_entropy(TransRates['ti'][timeStart2/dt:timeEnd3/dt],time_range=TransRates["ipctx"][timeStart2/dt:timeEnd3/dt],freq_range=[0.00017,0.00036])
	se36,dfreq36,maxFreq36,perMax36 = spec_entropy(TransRates['ti'][timeEnd1/dt:(timeEnd1+480.)/dt],time_range=TransRates["ipctx"][timeEnd1/dt:(timeEnd1+500.)/dt],freq_range=[0.0001,0.00025])
	#se3,dfreq3,maxFreq1,perMax = spec_entropy(TransRates['ti'][timeStart/dt:timeEnd/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd/dt],freq_range=[0.00008,0.00020])

	ans = np.array([se31,se32,se33,se34,se35,se36])
	indnan = np.where(np.isnan(ans)==True)
	ans[indnan] = 1
	print ans
	indmin = np.where(ans==np.min(ans))[0]
	print indmin

	#PDFeatures[i][5] = ans[indmin]
	PDFeatures[0][5] = np.min(ans)

	#PDFeatures[i][5] = np.mean(ans)

	'''
	if se31 < se32:
		PDFeatures[i][5] = se31
		PDFeatures[i][6] = dfreq31
		#maxFreq[i][1] = maxFreq31
		#perPowerMaxFreq[i][1] = perMax31
	else:
		PDFeatures[i][5] = se32
		PDFeatures[i][6] = dfreq32
		#maxFreq[i][1] = maxFreq32
		#perPowerMaxFreq[i][1] = perMax32
	'''

	se41,dfreq41,maxFreq41,perMax41 =   spec_entropy(TransRates['gpi'][timeStart/dt:timeEnd1/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd1/dt],freq_range=[0.00009,0.00017])
	se42,dfreq42,maxFreq42,perMax42 =   spec_entropy(TransRates['gpi'][timeStart/dt:timeEnd2/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd2/dt],freq_range=[0.00007,0.00017])
	se43,dfreq43,maxFreq43,perMax43 =   spec_entropy(TransRates['gpi'][timeStart/dt:timeEnd1/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd1/dt],freq_range=[0.00017,0.00036])
	se44,dfreq44,maxFreq44,perMax44 =   spec_entropy(TransRates['gpi'][timeStart/dt:timeEnd2/dt],time_range=TransRates["ipctx"][timeStart/dt:timeEnd2/dt],freq_range=[0.00017,0.00036])
	se45,dfreq45,maxFreq45,perMax45 =   spec_entropy(TransRates['gpi'][timeStart2/dt:timeEnd3/dt],time_range=TransRates["ipctx"][timeStart2/dt:timeEnd3/dt],freq_range=[0.00017,0.00036])
	se46,dfreq46,maxFreq46,perMax46 = spec_entropy(TransRates['gpi'][timeEnd1/dt:(timeEnd1+480.)/dt],time_range=TransRates["ipctx"][timeEnd1/dt:(timeEnd1+500.)/dt],freq_range=[0.0001,0.00025])
	'''
	if se41 < se42:
		PDFeatures[i][7] = se41
	else:
		PDFeatures[i][7] = se42
	'''
	ans = np.array([se41,se42,se43,se44,se45,se46])
	indnan = np.where(np.isnan(ans)==True)
	ans[indnan] = 1
	print ans
	indmin = np.where(ans==np.min(ans))[0]
	print indmin
	#PDFeatures[i][7] = ans[indmin]
	PDFeatures[0][7] = np.min(ans)

	return PDFeatures



def paramSearch(d,anti=0):
	
	path = "/home/j.bahuguna/homology/Mallet/wojc1jc2/slowNormParams/newParams/output/"
	print "in Paramsearch"

	logging.basicConfig(level=logging.DEBUG)
	# Time trajectories
	leak = -0.1
	# Scaling all the known parameters by 3 times, to increase the range for unknown parameters
	knownparams = p.params["known"] 

	unknownparams = p.params["unknown"] 

	ValidParams=[]
	InValidParams=[]
	#numEpochs = 2500
	numEpochs = 300
	lenList = len(unknownparams['d1ta'])
	lenUnknowns = len(unknownparams)	
	#elmt = [np.random.randint(0,lenList,lenUnknowns) for i in xrange(numEpochs)] 			
	#elmt = pickle.load(open(path+"Combinations_20.pickle","r"))
	elmt1 = pickle.load(open(path+"uniqueLastIter_GSSO.pickle","r"))
	np.random.shuffle(elmt1)
	elmt = elmt1[:2000]

	newrandom = 0
	#Generate numEpochs combinations
	for epoch in xrange(4000):
		print "epoch",epoch
		if newrandom == 1:
			elmt = [np.random.randint(0,lenList,lenUnknowns) for i in xrange(numEpochs)] 	
		Grades = np.zeros(len(elmt))
		antiPDlist = []
		if epoch > 5: # Save the last comination so that we have a seed for next GA, stupid cluster has a limit of 24 hours
			pickle.dump(elmt,open(path+"LastComb_GSSO_BL.pickle","w"))
		for i,ind in enumerate(elmt):

			d1ta = unknownparams['d1ta'][ind[0]]
			d2ta = unknownparams['d2ta'][ind[1]]
			fsita = unknownparams['fsita'][ind[2]]
			fsiti = unknownparams['fsiti'][ind[3]]
			tata = unknownparams['tata'][ind[4]]
			tati = unknownparams['tati'][ind[5]]
			tastn = unknownparams['tastn'][ind[6]]
			tita = unknownparams['tita'][ind[7]]
			titi = unknownparams['titi'][ind[8]]
			tistn = unknownparams['tistn'][ind[9]]
			stnta = unknownparams['stnta'][ind[10]]
			stnti = unknownparams['stnti'][ind[11]]			
			tid2 = unknownparams['tid2'][ind[12]]
			tad2 = unknownparams['tad2'][ind[13]]	
			d1ti = unknownparams['d1ti'][ind[14]]
			d2ti = unknownparams['d2ti'][ind[15]]
			jc1 = unknownparams['jc1'][ind[16]]
			jc2 = unknownparams['jc2'][ind[17]]
			#jc2 = jc1 # Prevent trivial solutions
			jfsictx = unknownparams['jfsictx'][ind[18]]
			jstnctx = unknownparams['jstnctx'][ind[19]]
			'''	
			d1d1 = unknownparams['d1d1'][ind[20]]
			d1d2 = unknownparams['d1d2'][ind[21]]
			d2d1 = unknownparams['d2d1'][ind[22]]
			d2d2 = unknownparams['d2d2'][ind[23]]
			d2fsi = unknownparams['d2fsi'][ind[24]]
			d1fsi = unknownparams['d1fsi'][ind[25]]
			gpid1 = unknownparams['gpid1'][ind[26]]
			gpiti = unknownparams['gpiti'][ind[27]]
			gpita = unknownparams['gpita'][ind[28]]
			gpistn = unknownparams['gpistn'][ind[29]]
			'''
			#if np.abs(d1ti) >= np.abs(d1ta)  or np.abs(d2ti) >= np.abs(d2ta) or np.abs(stnta) >= np.abs(stnti) or np.abs(fsita) >np.abs(fsiti):
			#	continue
			# Dont add leak here, since the leak term shoudl be outside nonlinear function in the differential equation
			A = np.matrix([[knownparams['d1d1'],knownparams['d1d2'],knownparams['d1fsi'],d1ta,d1ti,0.,0.],[knownparams['d2d1'],knownparams['d2d2'],knownparams['d2fsi'],d2ta,d2ti,0.,0.],[0.,0.,knownparams['fsifsi'],fsita,fsiti,0.,0.],[0,tad2,0.,tata,tati,tastn,0],[0.,tid2,0.,tita,titi,tistn,0.],[0.,0.,0.,stnta,stnti,knownparams['stnstn'],0.],[knownparams['gpid1'],0.,0.,knownparams['gpita'],knownparams['gpiti'],knownparams['gpistn'],knownparams['gpigpi']]])
			#print A
			B = np.matrix([jc1,jc2,jfsictx,0,0,jstnctx,0])
			delay = 1.0	
			#Calculate Rates for SWA and Control
			ipctx = dict()
			ipctx["ip"]=np.zeros((1,2001))	
			#Calculate Rates for SWA and lesion(dopamine depletion)
			Flags = []
			Flags.append("Trans")
			#SWADopDepRates = calcRates(Flags,delay,A,B,False,ipctx,iptau=14.)
			TransRates = calcRates(Flags,delay,A,B,False,ipctx,iptau=p.params["iptau"],ipamp=4.)

			# Calculate Rates for Activation and Lesion
			#Flags = []
			#Flags.append("Act")
			#ActDopDepRates = calcRates(Flags,delay,A,B,False,ipctx,iptau=p.params["iptau"])

			# Checks Refer Figure 6I and 6J of Mallet 2008
			tests = np.zeros(3)

			PDF = calc_GSSO(TransRates)
			PDFPP = fs.postProcess(PDF,"PD")
			print "PDFPP",PDFPP
			#if np.round(np.mean(SWADopDepRates['ti'])) >= 19 and np.round(np.mean(SWADopDepRates['ti']))<=35: 				# Mean around 24, so +- 4Hz allowed
			if PDFPP[0][0] < -0.7: 				# Mean around 24, so +- 4Hz allowed
				tests[0] = 1
			
			#if np.mean(ActDopDepRates['ta']) > np.mean(ActDopDepRates['ti']):
			#if np.mean(ActDopDepRates['ti']) >= 10 and np.mean(ActDopDepRates['ti']) <18:		# Mean around 14
			if (1. - PDFPP[0][1]) > 0.45:		# Mean around 14
				tests[1] = 1

			#if np.mean(SWADopDepRates['ti']) > np.mean(ActDopDepRates['ti']):
			#if np.mean(ActDopDepRates['ta']) > 16 and np.mean(ActDopDepRates['ta']) <=23: # Mean around 19 # 
			
			# Since this is PD model, check D1 activity < D2 activity
			#if np.mean(ActDopDepRates['d2']) > np.mean(ActDopDepRates['d1']):
			# Sanity test , all rates are fairly above zero
			if np.mean(TransRates['d1'][100./p.params["dt"]:]) > 0.1 and np.mean(TransRates['d2'][100./p.params["dt"]:]) > 0.1 and np.mean(TransRates['fsi'][100./p.params["dt"]:]) > 0.1 and	np.mean(TransRates['ta'][100./p.params["dt"]:]) > 1.0 and np.mean(TransRates['ti'][100./p.params["dt"]:]) > 1.0 and np.mean(TransRates['stn'][100./p.params["dt"]:]) > 1.0 and np.mean(TransRates['gpi'][100./p.params["dt"]:]) > 0.1:
				tests[2] = 1
		#	if anti==0:
			print "tests",tests	
			print ind
			print "Trans:d1,d2,fsi,ta,ti,stn,gpi,tha",np.mean(TransRates["d1"]),np.mean(TransRates["d2"]),np.mean(TransRates["fsi"]),np.mean(TransRates["ta"]),np.mean(TransRates["ti"]),np.mean(TransRates["stn"]),np.mean(TransRates["gpi"]),np.mean(TransRates["tha"])
			Grades[i] = np.sum(tests)	
		
		# Select the ones with the higest grades
		# Consider both 11 and 12 here , but strictly 12 in findDist, so that the probability of finding combinations are incraesed.
		cutoff = 2
		sorted_list = sorted(zip(Grades,elmt),reverse=True,key=lambda x:x[0])
		#nextgen = [sorted_list[i] for i in xrange(len(sorted_list)) if sorted_list[i][0]>=cutoff]
		if epoch < 5:
			nextgen = [sorted_list[i] for i in xrange(len(sorted_list)) if sorted_list[i][0]>cutoff]
		else:
			nextgen = [sorted_list[i] for i in xrange(len(sorted_list)) if sorted_list[i][0]>cutoff]
		no2s = len([e[0] for e in nextgen if e[0] == 2.])
		no3s = len([e[0] for e in nextgen if e[0] == 3.])
		#indices = np.array([i for i,e in enumerate(nextgen) if e[0] >= 12.]) 
		indices = np.array([i for i,e in enumerate(nextgen) if e[0] > 2.]) 
		
		print indices
		'''
		only10s = []
		if len(indices) >0:	
			only10s = nextgen[indices] 
		'''	
		print "no3s",no3s
#		print "no11ss",no11s

		#print "nextgen",nextgen
		if epoch%1 == 0:
			pickle.dump(nextgen,open(path+"Combinations_GSSO_BL"+str(epoch+0)+".pickle","w"))
			#pickle.dump(only10s,open(path+"Combinations_"+str(epoch)+".pickle","w"))
		#Generate numEpochs combinations from these by random crossovers
	#	howmany = [np.random.randint(0,lenUnknowns) for i in xrange(numEpochs)]
		#Keep crossover % as 1 in this case, 1/12*100 = 8%
		if len(nextgen) > 0:
			# Changed this to get a new set of combinations, since this grid has a limit of 24 hours 
			howmany = 2	
			#howmany = 3	
			which1 = [np.random.randint(0,len(nextgen)) for i in xrange(numEpochs/2)]	 	
			which2 = [np.random.randint(0,len(nextgen)) for i in xrange(numEpochs/2)]	 	
			#print "which1",which1
			starts = [np.random.randint(0,lenUnknowns) for i in xrange(numEpochs/2)]		
			newSet = []

			if len(indices) >= 2:
				for i in xrange(0,numEpochs/2,1):
					#print nextgen[which1[i]]
					temp1 = np.copy(nextgen[which1[i]][1])		
					temp2 = np.copy(nextgen[which2[i]][1])
					#print "temp1",temp1
					#print "temp2",temp2
					#print "starts[i]",starts[i]
					temp3 = np.copy(temp1[starts[i]:starts[i]+howmany])
					if starts[i]+howmany < len(temp1):
					#print "temp3",temp3
						temp1[starts[i]:starts[i]+howmany] = np.copy(temp2[starts[i]:starts[i]+howmany])
						temp2[starts[i]:starts[i]+howmany] = temp3	
					#print "newtemp1",temp1
					#print "newtemp2",temp2
					newSet.append(temp1)
					newSet.append(temp2)
				#  0.1% mutation, 1 out of every 1000
				randNo = 40
				for x in xrange(randNo):
					mutset = np.random.randint(0,len(newSet))
					mutbit = np.random.randint(0,lenUnknowns)
					newSet[mutset][mutbit] = np.random.randint(0,lenList)


			else:
				# If there is only 1 element, use the same element, say 10 times, flip a random bit and add to newSet
				morerand = 20
				newSet.append(nextgen[0][1])
				for i in xrange(morerand):
					mutbit = np.random.randint(0,lenUnknowns)
					temp = np.copy(nextgen[0][1])
					temp[mutbit] = np.random.randint(0,lenList)
					newSet.append(temp)
	 
			prev = np.copy(elmt)
			elmt = np.copy(newSet)
		
			gc.collect()
			newrandom=0
		else:
			newrandom = 1
			continue
	
	return elmt												


tempipc = np.zeros((1,1001))
dtt = p.params["dtTF"]
tGt = np.arange(0.0,len(tempipc[0])+dtt,dtt)
timet = np.arange(0,len(tGt),1)

ipFC = np.zeros((len(timet)))
noise = np.random.uniform(low=-0.1,high=0.1,size=len(ipFC))
#tau = 5.
#tau = 20.
tau = 10.
#expKern = np.exp(-np.arange(0,50,dtt)/tau)
expKern = np.exp(-np.arange(0,100,dtt)/tau)
LFPnoise = np.convolve(noise,expKern,mode='same')
ipFC = np.copy(LFPnoise)+1.

ipFC[np.where(ipFC<0)]=0.0

#--------------------------------------------------------
timeD = np.arange(0,1+dtt,dtt)
ipD = np.zeros(len(timeD))
ipD[20:80] = 99999999

#--------------------------------------------------------


def RMS(T,sig):
	integral = np.sum(sig**2)
	return np.sqrt((1./float(T))*integral)



def S(x,theta,Qmax,a):
	#sigma=4.
	#sigma=4.
	sigma=1.
	#funcVal = (Qmax/(1.+(np.exp(-a*x/Qmax)*(Qmax-Qbase)/Qbase) ))
	funcVal = Qmax*(1./(1.+np.exp(-a*(x-theta)/sigma)))
	return funcVal 	
	#return x


def getipFC(tG):
        dt = p.params["dtTF"]
#       print "t",tG/dt
#       print ipFC
#       print ipFC[tG/dt]
        return ipFC[tG/dt]

def ipDiffFreqs(f,t):
        ipctx =2*np.sin(2.0*np.pi*f*t) +2.0
#       print "ipctx",ipctx
        return ipctx


def ipSWA(t):
#	if t >=500 and t <=1500:
#		x = 5.0
#	else:
#		x = 0.0
	ipctx =2*np.sin(2.0*np.pi*0.002*t) +2.0
#	print "ipctx",ipctx
	return ipctx

def ipT(t,ipamp):
	if t >=500 and t <=1500:
		x = ipamp
	else:
		x = 0.0
	return x

def ipTFreq(t,ipamp):
	return ipamp

def ipAct(t):
	ipctx = 2*np.sin(2.0*np.pi*0.02*t)+2.5
#	print "ipctx",ipctx
	return ipctx

def getipD(tG):
	dt = p.params["dtTF"]
	return ipD[tG/dt]

def func(Rates,timeGrid,knownparams,unknownparams,time,Flag,ipamp,ipfreq,iptau):
	leak1 = -1
	tau = iptau
#	print "timeGrid",timeGrid
#	print "time",time
	ip = 0
	if Flag == "SWA":
		ip = ipSWA(timeGrid)
	if Flag == "Trans":
		ip = ipT(timeGrid,ipamp)
	if Flag == "TransFreq":
		ip = ipTFreq(timeGrid,ipamp)

	if Flag == "Act":
		ip = ipAct(timeGrid)
        if Flag == 'funcConn':
                #ip = ipFC[timeGrid]
                ip = getipFC(timeGrid)
        if Flag == 'DiffFreq':
                ip = ipDiffFreqs(ipfreq,timeGrid)

	if Flag == "delta":
		ip = getipD(timeGrid)	
#	print "ip",ip
	z1 = Rates[0]*knownparams['d1d1'] + Rates[1]*knownparams['d1d2'] + knownparams['d1fsi']*Rates[2] + unknownparams['jc1']*ip + Rates[3]*unknownparams['d1ta']+ Rates[4]*unknownparams['d1ti']
	#d1bydt = (1./tau)*leak1*Rates[0] + (1./tau)*S(z1,0.05,75)
	#d1bydt = (1./tau)*leak1*Rates[0] + (1./tau)*S(z1,0.1,90)
	d1bydt = (1./tau)*leak1*Rates[0] + (1./tau)*S(z1,40.,65,0.1)
	#d1bydt = leak*Rates[0] + S(z1,5,leak=0.15)

	z2 = Rates[1]*knownparams['d2d2'] + Rates[0]*knownparams['d2d1'] + knownparams['d2fsi']*Rates[2] +unknownparams['jc2']*ip + Rates[3]*unknownparams['d2ta']+Rates[4]*unknownparams['d2ti']	
	#d2bydt = (1./tau)*leak1*Rates[1]+ (1./tau)*S(z2,0.05,75)
	#d2bydt = (1./tau)*leak1*Rates[1]+ (1./tau)*S(z2,0.1,90)
	d2bydt = (1./tau)*leak1*Rates[1]+ (1./tau)*S(z2,40.,65,0.1)
	#d2bydt = leak*Rates[1]+ S(z2,5.,leak=0.15)

	z3 = Rates[3]*unknownparams['fsita'] + Rates[4]*unknownparams['fsiti']+unknownparams['jfsictx']*ip + Rates[2]*knownparams['fsifsi']	
	#dfsibydt = leak1*Rates[2]+S(z3,0.1,80)
	#dfsibydt = (1./tau)*leak1*Rates[2]+(1./tau)*S(z3,10,50)
	#dfsibydt = (1./tau)*leak1*Rates[2]+(1./tau)*S(z3,30,100)
	dfsibydt = (1./tau)*leak1*Rates[2]+(1./tau)*S(z3,20.,80,0.1)

	z4 = Rates[3]*unknownparams['tata'] + Rates[4]*unknownparams['tati'] + Rates[5]*unknownparams['tastn'] + Rates[1]*unknownparams['tad2']#+Rates[7]*0.1
	#dtabydt = leak1*Rates[3]+ S(z4,0.5,50)
	#dtabydt = (1./tau)*leak1*Rates[3]+ (1./tau)*S(z4,0.4,55)
	#dtabydt = (1./tau)*leak1*Rates[3]+ (1./tau)*S(z4,0.4,65)
	dtabydt = (1./tau)*leak1*Rates[3]+ (1./tau)*S(z4,6.,50.,0.25)
	#dtabydt = (1./tau)*leak1*Rates[3]+ (1./tau)*S(z4,0.4,100)
	#dtabydt = (1./tau)*leak1*Rates[3]+ (1./tau)*S(z4,0.4,85)

	z5 = Rates[3]*unknownparams['tita'] + Rates[4]*unknownparams['titi'] + Rates[5]*unknownparams['tistn'] + Rates[1]*unknownparams['tid2']#+Rates[7]*0.1
	#dtibydt = leak1*Rates[4]+S(z5,0.5,100)
	#dtibydt = (1./tau)*leak1*Rates[4]+(1./tau)*S(z5,0.4,100)
	#dtibydt = (1./tau)*leak1*Rates[4]+(1./tau)*S(z5,0.4,110)
	dtibydt = (1./tau)*leak1*Rates[4]+(1./tau)*S(z5,6.,150.,0.21)
	#dtibydt = (1./tau)*leak1*Rates[4]+(1./tau)*S(z5,0.4,200)
	#dtibydt = (1./tau)*leak1*Rates[4]+(1./tau)*S(z5,0.4,135)

 	z6 = unknownparams['jstnctx']*ip + Rates[4]*unknownparams['stnti'] + Rates[3]*unknownparams['stnta'] +Rates[5]*knownparams['stnstn']
	#dstnbydt = (1./tau)*leak1*Rates[5]+(1./tau)*S(z6,0.4,150)
	#dstnbydt = (1./tau)*leak1*Rates[5]+(1./tau)*S(z6,0.38,500)
	dstnbydt = (1./tau)*leak1*Rates[5]+(1./tau)*S(z6,15.,500,0.25)

	z7 = Rates[0]*knownparams['gpid1']+Rates[3]*knownparams['gpita']+ Rates[4]*knownparams['gpiti'] + Rates[5]*knownparams['gpistn'] + Rates[6]*knownparams['gpigpi']
	#dgpibydt = (1./tau)*leak1*Rates[6]+(1./tau)*S(z7,0.5,100)
	dgpibydt = (1./tau)*leak1*Rates[6]+(1./tau)*S(z7,35.,250,0.1)

        #z8 = Rates[6]*-0.9 + 10
        z8 = 1
        dthabydt = (1./tau)*leak1*Rates[7]+(1./tau)*S(z8,3,10,20)


	#dgpibydt = leak*Rates[6]+S(z7,150.,leak=0.15)
	return [d1bydt,d2bydt,dfsibydt,dtabydt,dtibydt,dstnbydt,dgpibydt,dthabydt]


def calcRates(Flags,d,A,B,fourier,ipctx1,ipamp=5.0,ipfreq=2.,iptau=1,scale=1):
	#leak = -0.05
	#leak = -0.1
	leak = -0.15
	if d == 1:
		knownparams = p.params["known"].copy() # Normal 
	if d == 2:
		knownparams = p.params["known"].copy() # Short term plasticity
		knownparams['gpid1'] = knownparams['gpid1']*2
	
	unknownparams = dict()
	unknownparams['d1ta'] = A[0,3]*scale
	unknownparams['d2ta'] = A[1,3]*scale
	unknownparams['fsita'] = A[2,3]*scale
	unknownparams['fsiti'] = A[2,4]*scale
	unknownparams['tata'] = A[3,3]*scale
	unknownparams['tati'] = A[3,4]*scale
	unknownparams['titi'] = A[4,4]*scale
	unknownparams['tita'] = A[4,3]*scale
	unknownparams['stnti'] = A[5,4]*scale
	unknownparams['stnta'] = A[5,3]*scale
	unknownparams['tastn'] = A[3,5]*scale
	unknownparams['tistn'] = A[4,5]*scale
	unknownparams['tid2'] = A[4,1]*scale
	unknownparams['tad2'] = A[3,1]*scale
	unknownparams['d1ti'] = A[0,4]*scale
	unknownparams['d2ti'] = A[1,4]*scale
	unknownparams['jc1'] = B[0,0]*scale
	unknownparams['jc2'] = B[0,1]*scale
	unknownparams['jfsictx'] = B[0,2]*scale
	unknownparams['jstnctx'] = B[0,5]*scale

	#print "knownparams",knownparams
	#print "unknownparams",unknownparams
	'''
	unknownparams['d1d1']  =A[0,0] 
	unknownparams['d1d2']  =A[0,1] 
	unknownparams['d2d1']  =A[1,0]
	unknownparams['d2d2']  =A[1,1]
	unknownparams['d2fsi'] =A[1,2]
	unknownparams['d1fsi'] =A[0,2]
	unknownparams['gpid1'] =A[6,0]
	unknownparams['gpiti'] =A[6,4]
	unknownparams['gpita'] =A[6,3]
	unknownparams['gpistn']=A[6,5]
	'''
	# Leak isnt considered for d1,d2,fsi,stn,gpi here, so include for them in equations!!!
	dt = p.params["dt"]
        timeGrid = np.arange(0.0,len(ipctx1["ip"][0])+dt,dt)
	time = np.arange(0,len(timeGrid),1)
	ipctx = np.zeros((len(time)))
	frate = 0.0
	#print "ipctx",ipctx
	for which in Flags:
			# Simulating dopamine depletion
		
		if which == 'SWA':
			# Frate = 1/0.004 = 250
			#ipctx[0] =5*np.sin(2.0*np.pi*0.003*time) +5.0 
			# time units = msec, so 2*pi*f , f is in cycles/msec = 2Hz
			ipctx[:] =2*np.sin(2.0*np.pi*0.002*timeGrid) +2.0
			#ipctx[0] = 0.0
			frate = 250.	
			print "SWA"
		if which == 'Both':
			# Both STN and STR have normal values here
			#print "Ctrl Do nothing"
			continue
		if which == 'STRint':
			# By default STR is non-PD, so set STN to PD
			knownparams['jstnctx'] = 5.5
		if which == 'Trans':
			#ipctx[0] = 5.0	
			ipctx[500/dt:1500/dt]= ipamp	
         	if which == "NoisyTrans":
                        noise = np.random.uniform(low=-0.1,high=0.1,size=len(ipctx[500/dt:1500/dt]))
                        tau = 5.
                        expKern = np.exp(-np.arange(0,30,1)/tau)
                        LFPnoise = np.convolve(noise,expKern,mode='same')
                        #ipctx[0] = ipctx[0]+LFPnoise
                        #ipctx[200:1200] = 8+LFPnoise
                        ipctx[500/dt:1500/dt] = 5.0+noise
	
		if which == 'funcConn':
                        # Apparently the method to generate pink noise is:, amplitude spectrum varies as 1/f
			# Alternate code - found on internet in matlab
			'''
			Nx = 2^16;  % number of samples to synthesize
			B = [0.049922035 -0.095993537 0.050612699 -0.004408786];
			A = [1 -2.494956002   2.017265875  -0.522189400];
			nT60 = round(log(1000)/(1-max(abs(roots(A))))); % T60 est.
			v = randn(1,Nx+nT60); % Gaussian white noise: N(0,1)
			x = filter(B,A,v);    % Apply 1/F roll-off to PSD
			x = x(nT60+1:end);    % Skip transient response

			'''
                        freq = np.fft.fftfreq(len(ipctx))
                        #ampSpec = (0.1*np.random.uniform(0,1,len(freq)))/freq
			mult= 1./len(freq)
                        ampSpec = (mult*np.random.uniform(0,2,len(freq)))/freq
                        timeSig = (1/mult)*np.fft.ifft(ampSpec[1:])
                        ipctx[1:] = np.abs(timeSig)

		if which == 'STNint':
			# Set STR to PD
			knownparams['jc1'] = 7.5 # LTP breaks down in D1
			knownparams['jc2'] = 8.5 # LTD breaks down in D2

		if which == 'Act':
			# Frame rate = 1/0.01 = 100
			#ipctx[0] = 5.0*np.sin(2.0*np.pi*0.006*time)+8.0
			# Frequency here is 10 Hz
			ipctx[:] = 2*np.sin(2.0*np.pi*0.02*timeGrid)+2.5 
			frate = 100.
                if which == "DiffFreq":
                        ipctx[:] = 2*np.sin(2.0*np.pi*(ipfreq/1000.)*timeGrid)+2.0

	# These values were tuned such that no firing rates go to zero
	lamd1 = 0
	lamd2 = 0
	lamfsi =0
	lamgpi =0 #All these nuclei have tonic firing    # initial conditions - fixed point
	lamstn =0
	lamta = 0 
	lamti = 0#lamta = 0.0 

	initRates = np.ones((8))*1
	#print "knownparams",knownparams
	#print "unknownparams",unknownparams
#	print "which",which
	finalRates = odeint(func,initRates,timeGrid,hmax=0.1,args = (knownparams,unknownparams,time,which,ipamp,ipfreq/1000.,iptau))	
	
	#print "finalRates",finalRates
				
	Rates = dict()
	Rates['d1'] = finalRates[:,0]
	Rates['d2'] = finalRates[:,1]
	Rates['fsi'] = finalRates[:,2]
	Rates['ta'] = finalRates[:,3]
	Rates['ti'] = finalRates[:,4]
	Rates['stn'] = finalRates[:,5]
	Rates['gpi'] = finalRates[:,6]	
	Rates['tha'] = finalRates[:,7]	
	Rates['A'] = A
	if which == 'funcConn':
		Rates['ipctx'] = ipFC
	else:
		Rates['ipctx'] = ipctx
	#print "Rates",Rates
	# Phase difference found by cross correlogram
	# Ignore first 100 msecs/timesteps to ignore transients
	#print np.shape(ipctx[1000:])
	#print np.shape(finalRates[:,5][1000:])
	if which != 'funcConn':
		Rates['stn_ctx'] = np.corrcoef(ipctx[1000/dt:],finalRates[:,5][1000/dt:])[0][1]	
		Rates['stn_ta'] = np.corrcoef(finalRates[:,3][1000/dt:],finalRates[:,5][1000/dt:])[0][1]	
		Rates['stn_ti'] = np.corrcoef(finalRates[:,4][1000/dt:],finalRates[:,5][1000/dt:])[0][1]	
		Rates['taFF'] = np.var(Rates['ta'][1000/dt:])/np.mean(Rates['ta'][1000/dt:])
		Rates['tiFF'] = np.var(Rates['ti'][1000/dt:])/np.mean(Rates['ti'][1000/dt:])	

	'''
	if fourier == True:
		fft_ti = np.fft.fft(Rates['ti'][:len(Rates['ipctx'][0])])
		fft_ta = np.fft.fft(Rates['ta'][:len(Rates['ipctx'][0])])
		fft_stn = np.fft.fft(Rates['stn'][:len(Rates['ipctx'][0])])
		fft_ctx = np.fft.fft(Rates['ipctx'][0])
		#dt = Rates['ipctx'][0][1]-Rates['ipctx'][0][0]
			
		freqs = np.fft.fftfreq(len(Rates['ipctx'][0]))
		indc = np.argmax(np.abs(fft_ctx[1:]))
		inds = np.argmax(np.abs(fft_stn[1:-1]))
		freq = freqs[indc]
		freq_hz = abs(freq*frate)
		# Return the phase at the index of cortical input	
		Rates['fft_ti_c'] = np.angle(fft_ti[indc])
		Rates['fft_ta_c'] = np.angle(fft_ta[indc])
		Rates['fft_stn_c'] = np.angle(fft_stn[indc])
		Rates['fft_ctx_c'] = np.angle(fft_ctx[indc])

		Rates['fft_ti_s'] = np.angle(fft_ti[inds])
		Rates['fft_ta_s'] = np.angle(fft_ta[inds])
		Rates['fft_stn_s'] = np.angle(fft_stn[inds])
		Rates['fft_ctx_s'] = np.angle(fft_ctx[inds])
	'''
	return Rates 





def plotTime(Rates,tit,Fourier): 
	from matplotlib import *
	time = np.arange(0,2000,1.)
	fig = pl.figure()
	pl.title('Time dependent behavior- '+tit)
	Ax = pl.gca()
	Ax.set_xticklabels(Ax.get_xticklabels(),visible=False)
	Ax.set_yticklabels(Ax.get_yticklabels(),visible=False)

	t1 = fig.add_subplot(8,1,1)
	t1.plot(time,Rates['d1'][:len(time)],'b-',label='D1',linewidth=1.5)
	setp(t1.get_xticklabels(),visible=False)
	for x in t1.get_yticklabels()[::2]:
		x.set_visible(False)
	t1.legend()

	t2 = fig.add_subplot(8,1,2,sharex=t1)
	setp(t2.get_xticklabels(),visible=False)
	t2.plot(time,Rates['d2'][:len(time)],'r-',label='D2',linewidth=1.5)
	#setp(t.get_yticklabels(),visible=False)
	for x in t2.get_yticklabels()[::2]:
		x.set_visible(False)

	t2.legend()

	t3 =fig.add_subplot(8,1,3,sharex=t1)
	t3.plot(time,Rates['fsi'][:len(time)],'g-',label='FSI',linewidth=1.5)
	setp(t3.get_xticklabels(),visible=False)
	for x in t3.get_yticklabels()[::2]:
		x.set_visible(False)

	#setp(t.get_yticklabels(),visible=False)
	t3.legend()

	t4 = fig.add_subplot(8,1,4,sharex=t1)
	t4.plot(time,Rates['ta'][:len(time)],'b-',label='GPe-TA',linewidth=1.5)
	setp(t4.get_xticklabels(),visible=False)
	for x in t4.get_yticklabels()[::2]:
		x.set_visible(False)

	#setp(t.get_yticklabels(),visible=False)
	t4.legend()

	t5 = fig.add_subplot(8,1,5,sharex=t1)
	t5.plot(time,Rates['ti'][:len(time)],'b-',label='GPe-TI',linewidth=1.5)
	setp(t5.get_xticklabels(),visible=False)
	for x in t5.get_yticklabels()[::2]:
		x.set_visible(False)

	#setp(t.get_yticklabels(),visible=False)
	t5.legend()

	t6 = fig.add_subplot(8,1,6,sharex=t1)
	t6.plot(time,Rates['stn'][:len(time)],'k-',label='STN',linewidth=1.5)
	setp(t6.get_xticklabels(),visible=False)
	for x in t6.get_yticklabels()[::2]:
		x.set_visible(False)

	#setp(t.get_yticklabels(),visible=False)
	t6.legend()

	#pl.savefig('Recovery_DBS_test.pdf')
	t7 = fig.add_subplot(8,1,7,sharex=t1)
	t7.plot(time,Rates['gpi'][:len(time)],'k-',label='Gpi',linewidth=1.5)
	setp(t7.get_xticklabels(),visible=False)
	for x in t7.get_yticklabels()[::2]:
		x.set_visible(False)

	#setp(t.get_yticklabels(),visible=False)
	t7.legend()

	t8 = fig.add_subplot(8,1,8,sharex=t1)
	t8.plot(time,Rates['ipctx'][0],'k-',label='Ctx',linewidth=1.5)
	#setp(t8.get_xticklabels(),visible=False)
	for x in t8.get_yticklabels()[::2]:
		x.set_visible(False)

	#setp(t.get_yticklabels(),visible=False)
	t8.legend()
	pl.savefig(tit+"TimeDep"+".pdf")	
	
	if Fourier == True:
		
		fig1 = pl.figure()
		# Fourier components analysis
		fft_ti = np.fft.fft(Rates['ti'][:len(Rates['ipctx'][0])])
		fft_ta = np.fft.fft(Rates['ta'][:len(Rates['ipctx'][0])])
		fft_stn = np.fft.fft(Rates['stn'][:len(Rates['ipctx'][0])])
		fft_ctx = np.fft.fft(Rates['ipctx'][0])

		freqs = np.fft.fftfreq(len(Rates['ipctx'][0]),Rates['ipctx'][0][1]-Rates['ipctx'][0][0])
		t9 = fig1.add_subplot(211)
		t9.set_title(tit+' Fourier Magnitude')
		t9.plot(freqs,np.abs(fft_ti),'b',label='TI')
		t9.plot(freqs,np.abs(fft_ta),'r',label='TA')
		t9.plot(freqs,np.abs(fft_stn),'g',label='STN')
		#t9.plot(freqs,np.abs(fft_ctx),'k',label='Ctx')
		t9.set_xlim(-0.15,0.15)
		t9.legend()

		t10 = fig1.add_subplot(212)
		t10.set_title(tit+' Fourier Phase') 
		t10.plot(freqs,np.angle(fft_ti),color='b',marker='.',label='TI')
		t10.plot(freqs,np.angle(fft_ta),color='r',marker='.',label='TA')
		t10.plot(freqs,np.angle(fft_stn),color='g',marker='.',label='STN')	
		#t10.plot(freqs,np.angle(fft_ctx),color='k',marker='^',label='Ctx')
#		t10.set_xlim(-0.15,0.15)
		t10.legend()
		pl.savefig("Fourier"+tit+".pdf")	
		




def diffD1D2(Flags):
	# To check if the difference between D1 and D2 amplifies downstream
	# First decide which model to use
	delay = 1
	if Flags == "Allsym":
		(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
		# D = Direct pathway, ID = Indirect pathway, HD = Hyperdirect pathway
		# Reducing a full recurrent matrix leads to postive and negative contributions in ID and HD instead of pure just positive contributions
		D = params['gpid1']
		print "Direct",D
		
		de1 = 1. + (params['d1d1']*params['fsifsi']) - (params['stnti']*params['stnstn'])
		Ex1 = (params['stnti']*params['d1d1']*params['fsifsi']*params['gpistn'])/de1  		
		Ex2 = (params['gpid1']*params['stnstn']*params['d1ta']*params['fsifsi'])/de1		
		IDpos = params['stnti']*params['tid2']*(params['d1ta']*params['gpid1']*params['tistn']+ Ex1 + Ex2)
		
		print "IDpos",IDpos

		Ex3 = (params['d1ta']+params['d1ta']*params['tata']+((params['stnta']*params['fsiti']*params['d1fsi'])/de1))
		IDneg = params['gpid1']+params['gpiti']*params['tid2']+params['gpid1']*params['stnstn']*params['tid2']*Ex3	
		print "IDneg",IDneg

		HDpos = (params['jstnctx']*params['gpid1']*params['stnstn']*params['fsiti']*params['d1fsi'])/de1
		print "HDpos",HDpos
		Ex4 = params['jstnctx']*params['d1d1']*params['fsifsi']*params['stnti']*params['gpistn']
		Ex5 = params['jstnctx']*params['gpid1']*params['stnstn']*params['d1ta']*params['fsifsi']
		HDneg = (Ex4 + Ex5)/de1	
		print "HDneg",HDneg

		d1fix = np.mean(d1[:-10])
		d2fix = np.mean(d2[:-10])
		DelMSN = d1fix - d2fix
		DelGpi = (D*d1fix) + ((IDpos - IDneg)*d2fix)

	return (DelMSN,DelGpi)			

def stabilityDiffData():
	delay=1
	Flags = []
	Flags.append('none')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	time = np.arange(0.0,2000.0,1.0)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Normal Conditions',False)

	#(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B) = calcRates('gpeAsymm')
	#plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time)

	#(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B) = calcRates('stngpe')
	#plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time)
	Flags = []
	Flags.append('mallet')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Bias from Mallet',False)

	Flags = []
	Flags.append('mastro')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Norm- Mastro',False)

	Flags=[]
	Flags.append('Allsym')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Norm - Allsym',False)

	Flags = []
	Flags.append('mastro')
	Flags.append('dopdep')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Dop Dep-Mastro',False)

	Flags=[]
	Flags.append('dopdep')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Dop Dep - Norm',False)

	Flags=[]
	Flags.append('mallet')
	Flags.append('dopdep')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Dop Dep - Mallet',False)

	Flags=[]
	Flags.append('Allsym')
	Flags.append('dopdep')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Dop Dep - Allsym',False)

	pl.show()

def checkPhaseRel():
	delay=1
	time = np.arange(0.0,2000.0,1.0)
	Flags = []
	Flags.append('none')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Original tid2 in Normal Model',True)
	Flags.append('tid2')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Depleted tid2 in Normal Model',True)


	Flags = []
	Flags.append('mallet')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Original tid2 in Mallet',True)
	Flags.append('tid2')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Depleted tid2 in Mallet',True)

	Flags = []
	Flags.append('mastro')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Normal tid2 in Mastro',True)
	Flags.append('tid2')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Depleted tid2 in Mastro',True)

	Flags = []
	Flags.append('Allsym')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Normal tid2 in Allsym Model',True)
	Flags.append('tid2')
	(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,params) = calcRates(Flags,delay)
	plotTime(d1,d2,fsi,ti,ta,stn,gpi,ipctx,A,B,time,'Depleted tid2 in Allsym Model',True)

	pl.show()


delay = 1.0
#elmt = paramSearch(delay)
#pickle.dump(elmt,open("Combinations_DopDep.pickle","w"))
'''
elmt = pickle.load(open("Combinations.pickle","r"))
	knownparams = {
	 
	'd1d1' : -0.7,
#	'd1d1' : -0.0,
	'd1d2' : -0.73,
#	'd1d2' : -0.0,
	'd2d1' : -0.16,
#	'd2d1' : -0.0,
	'd2d2' : -0.97,
#	'd2d2' : -0.0,
	'd2fsi' : -0.22,
#	'd2fsi' : -0.0,
	'd1fsi' : -0.324,
#	'd1fsi' : -0.0,
	'gpid1' : -8.9,
	'gpiti' : -0.17,
	'tid2' : -3.27,
	'gpistn' : 1.98,
	'tad2' : 0.0,
	'stnstn' : 0.001,
	'gpita' : 0.0,
	'gpigpi' : 0.0,
	'd1ti' : 0.0,
	'd2ti' : 0.0,
	'fsifsi':-0.0012,
	'jc1' : 7.5,
	'jc2' : 6.5,
	'jstnctx' : 4.5, # Trying to tri-phasic response in GPi
	'jfsictx' : 1.8
	}

	unknownparams = {
	'stnta' : np.arange(-0.01,-0.65,-0.15),
	#'stnta' : np.arange(-0.01,-0.05,-0.05),
	'stnti' : np.arange(-0.01,-0.65,-0.15),
	#'stnti' : np.arange(-0.01,-0.05,-0.05),
	'tistn' : np.arange(0.01,0.82,0.2),
	#'tistn' : np.arange(0.01,0.05,0.05),
	'tastn' : np.arange(0.01,0.82,0.2),
	#'tastn' : np.arange(0.01,0.05,0.05),
	'tata': np.arange(-0.01,-0.65,-0.15),
	#'tata': np.arange(-0.01,-0.05,-0.05),
	'tati': np.arange(-0.01,-0.65,-0.15),
	#'tati': np.arange(-0.01,-0.05,-0.05),
	'tita': np.arange(-0.01,-0.65,-0.15),
	#'tita': np.arange(-0.01,-0.05,-0.05),
	'titi': np.arange(-0.01,-0.65,-0.15),
	#'titi': np.arange(-0.01,-0.05,-0.05),
	'd1ta' : np.arange(-0.01,-0.65,-0.15),
	#'d1ta' : np.arange(-0.01,-0.05,-0.05),
	'd2ta' : np.arange(-0.01,-0.65,-0.15),
	#'d2ta' : np.arange(-0.01,-0.05,-0.05),
	'fsita' : np.arange(-0.01,-0.65,-0.15),
	#'fsita' : np.arange(-0.01,-0.05,-0.05),
	'fsiti' : np.arange(-0.01,-0.65,-0.15),
	'tid2' : np.arange(0,-5,-1),
	'tad2' : np.arange(0,-5,-1)

	#'fsiti' : np.arange(-0.01,-0.05,-0.05),
	}

for i,ind in enumerate(elmt):
	d1ta = unknownparams['d1ta'][ind[0]]
	d2ta = unknownparams['d2ta'][ind[1]]
	fsita = unknownparams['fsita'][ind[2]]
	fsiti = unknownparams['fsiti'][ind[3]]
	tata = unknownparams['tata'][ind[4]]
	tita = unknownparams['tita'][ind[5]]
	tastn = unknownparams['tastn'][ind[6]]
	tita = unknownparams['tita'][ind[7]]
	titi = unknownparams['titi'][ind[8]]
	tistn = unknownparams['tistn'][ind[9]]
	stnta = unknownparams['stnta'][ind[10]]
	stnti = unknownparams['stnti'][ind[11]]			
	A = np.matrix([[leak+knownparams['d1d1'],knownparams['d1d2'],knownparams['d1fsi'],d1ta,knownparams['d1ti'],0.,0.],[knownparams['d2d1'],leak+knownparams['d2d2'],knownparams['d2fsi'],d2ta,knownparams['d2ti'],0.,0.],[0.,0.,leak+knownparams['fsifsi'],fsita,fsiti,0.,0.],[0,knownparams['tad2'],0.,leak+tata,tita,tastn,0],[0.,knownparams['tid2'],0.,tita,leak+titi,tistn,0.],[0.,0.,0.,stnta,stnti,leak+knownparams['stnstn'],0.],[knownparams['gpid1'],0.,0.,knownparams['gpita'],knownparams['gpiti'],knownparams['gpistn'],leak+knownparams['gpigpi']]])

Flags = []
Flags.append("SWA")
Flags.append("Ctrl")
Rates = calcRates(Flags,delay,A)
plotTime(Rates,"SWA - Ctrl",True) 

Flags = []
Flags.append("SWA")
Flags.append("DopDep")
Rates = calcRates(Flags,delay,I[0])
plotTime(Rates,"SWA - DopDep",True) 

Flags = []
Flags.append("Act")
Flags.append("Ctrl")
Rates = calcRates(Flags,delay,I[0])
plotTime(Rates,"Act - Ctrl",True) 

Flags = []
Flags.append("Act")
Flags.append("DopDep")
Rates = calcRates(Flags,delay,I[0])
plotTime(Rates,"Act - DopDep",True) 
'''





