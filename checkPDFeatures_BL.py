#Feature here is different., Its the balance of excitation and inhibition for each bg nucleus.
# If required, other features will be added

# Right now 2 features have been identified. 1) How much GPi is supressed when the striatal activity is high
# 2) How much is the network suceptible to oscillilations. Determined by +ve real part of the complex conjugates
# Every matrix is tagged with a 2-feature vector, showing how the matrix has scored on both the features.



import pickle
import numpy as np
import pylab as pl
import matplotlib as mpl
mpl.use('Agg')


import matplotlib.cm as cm
from pylab import *
# Since its a sparse matrix
import scipy.sparse.linalg as sp
import scipy.fftpack as spfft
import itertools
import scipy.cluster.hierarchy as sph
import os
from pylab import *
#import paramsearchGA_DopDep as psGA
import paramsearchGA_DopDep_nonlinear_BaseLine as psGA
import knownUnknownParams as p

AllAs=[]
AllASTPs=[]
AllBs=[]
storage_home = '/home/j.bahuguna/homology/Mallet/wojc1jc2/slowNormParams/newParams'
from scipy.optimize import fsolve
ctx = 5.0
terms1 = ["d1","d2","fsi","ta","ti","stn","gpi","ipctx"]
def S(x,theta,Qmax):
	sigma=3.8
	funcVal = Qmax*(1./(1.+np.exp(-(x-theta)/sigma)))
	return funcVal 	
	#return x






def mypsd(Rates,time_range,bin_w = 5., nmax = 4000):

      #psd, max_value, freq,h = misc2.psd_sp(spikes[:,1],nr_bins,nr_neurons)
      #print time_range
      bins = np.arange(0,len(time_range),1)
      #print bins
      a,b = np.histogram(Rates, bins)
      ff = (1./len(bins))*abs(np.fft.fft(Rates- np.mean(Rates)))**2
      Fs = 1./(1*0.001)
      #freq2 = np.fft.fftfreq(len(bins),d=0.01)[0:len(bins/2)+1] # d= dt
      freq2 = np.fft.fftfreq(len(bins))[0:len(bins/2)+1] # d= dt
      #freq = np.linspace(0,Fs/2,len(ff)/2+1)
      #freq = np.fft.fftfreq(len(bins),d=0.01)[:len(ff)/2+1]
      freq = np.fft.fftfreq(len(bins))[:len(ff)/2+1]
      px = ff[0:len(ff)/2+1]
      max_px = np.max(px[1:])
      idx = px == max_px
      corr_freq = freq[pl.find(idx)]
      new_px = px
      max_pow = new_px[pl.find(idx)]
      return new_px,freq,corr_freq[0],freq2, max_pow


def spec_entropy(Rates,time_range=[],bin_w = 5.,freq_range = []):
	'''Function to calculate the spectral entropy'''

        power,freq,dfreq,dummy,dummy = mypsd(Rates,time_range,bin_w = bin_w)
        if freq_range != []:
                power = power[(freq>=freq_range[0]) & (freq <= freq_range[1])]
                freq = freq[(freq>=freq_range[0]) & (freq <= freq_range[1])]
		maxFreq = freq[np.where(power==np.max(power))]*1000*100
		perMax = (np.max(power)/np.sum(power))*100
        k = len(freq)
        power = power/sum(power)
        sum_power = 0
        for ii in range(k):
                sum_power += (power[ii]*np.log(power[ii]))
        spec_ent = -(sum_power/np.log(k))
        return spec_ent,dfreq,maxFreq,perMax



def amp_freq(timeSeries):
	freq = spfft.rfftfreq(len(timeSeries),1)
	fft = spfft.rfft(timeSeries)
        amp = np.abs(fft)
        indmax = np.where(amp==np.max(amp))[0][0]
        oi = (np.sum(amp[indmax-1:indmax+1]))/np.sum(amp)

	indmax = np.where(amp==np.max(amp))[0][0]
	dfreq = freq[indmax]*1000         # Sampling frequency = 1/1ms = 1/0.001= 1000
	
	return oi,dfreq

def classification(params):
	pathname = storage_home+'/output/'
	pathname1 = '/home/j.bahuguna/homology/Mallet/wojc1jc2/slowNormParams/newParams'+'/output/'
	print "in classification"
	knownparams = p.params["known"] 
	leak = -0.05
	Supressed=[]
	Sup_Ind=[]
	k = 0
	#print Allcombs
	#PDFeatures = np.zeros((len(Allcombs),2))
	# 0= akinesia, 1,2 = gpi amplitude spectrum,dominant frequency, 3,4 = TA amplitude,frequency, 5,6=TI amplitude, frequency
#	Samples = np.arange(0,len(Allcombs),1)
#	np.random.shuffle(Samples)
	randSamps = pickle.load(open(pathname+"randSamps_BL.pickle","r"))
	Allcombs = pickle.load(open(pathname+"Allcombs_BL.pickle","r"))
	#PDFeatures = np.zeros((len(randSamps),8))
	PDFeatures = np.ones((len(randSamps),8))
	maxFreq = np.zeros((len(randSamps),3))
	perPowerMaxFreq = np.zeros((len(randSamps),3))
	ipAmp = params["ipAmp"]
	print ipAmp
	baseLineFR = []
	for i,j in enumerate(randSamps):
		print i
		ind = Allcombs[j]
		d1ta = ind[0]
		d2ta = ind[1]
		fsita = ind[2]
		fsiti = ind[3]
		tata = ind[4]
		tati = ind[5]
		tastn = ind[6]
		tita = ind[7]
		titi = ind[8]
		tistn = ind[9]
		stnta = ind[10]
		stnti = ind[11]			
		tid2 = ind[12]
		tad2 = ind[13]	
		d1ti = ind[14]
		d2ti = ind[15]
		jc1 = ind[16]
		jc2 = ind[17]
		jfsictx = ind[18]
		jstnctx = ind[19]

		#A = np.matrix([[knownparams['d1d1'],knownparams['d1d2'],knownparams['d1fsi'],d1ta,knownparams['d1ti'],0.,0.],[knownparams['d2d1'],knownparams['d2d2'],knownparams['d2fsi'],d2ta,knownparams['d2ti'],0.,0.],[0.,0.,knownparams['fsifsi'],fsita,fsiti,0.,0.],[0,tad2,0.,tata,tati,tastn,0],[0.,tid2,0.,tita,titi,tistn,0.],[0.,0.,0.,knownparams['stnta'],stnti,knownparams['stnstn'],0.],[knownparams['gpid1'],0.,0.,knownparams['gpita'],knownparams['gpiti'],knownparams['gpistn'],knownparams['gpigpi']]])
		A = np.matrix([[knownparams['d1d1'],knownparams['d1d2'],knownparams['d1fsi'],d1ta,d1ti,0.,0.],[knownparams['d2d1'],knownparams['d2d2'],knownparams['d2fsi'],d2ta,d2ti,0.,0.],[0.,0.,knownparams['fsifsi'],fsita,fsiti,0.,0.],[0,tad2,0.,tata,tati,tastn,0],[0.,tid2,0.,tita,titi,tistn,0.],[0.,0.,0.,stnta,stnti,knownparams['stnstn'],0.],[knownparams['gpid1'],0.,0.,knownparams['gpita'],knownparams['gpiti'],knownparams['gpistn'],knownparams['gpigpi']]])

		B = np.matrix([jc1,jc2,jfsictx,0,0,jstnctx,0])

		AllAs.append(np.array(A))
		AllBs.append(np.array(B))
		delay = 1.0	
		#Calculate Rates for SWA and Control
		ipctx1=dict()
		#Calculate Rates for SWA and lesion(dopamine depletion)
		Flags = []
		Flags.append("Trans")
		#Flags.append("DopDep")
		
		ipctx1["ip"] = np.zeros((1,2001))
		SWADopDepRates = psGA.calcRates(Flags,delay,A,B,False,ipctx1,ipAmp,iptau=p.params["iptau"])

		# Calculate Rates for Activation and Lesion
		# Set a threshold for Gpi rates == 1Hz,
		# Record the ratio of Gpi rates between 500-1000/Rates before 500
		dt = p.params["dt"]
		howmuch = (np.mean(SWADopDepRates['gpi'][100/dt:500/dt]) -np.mean(SWADopDepRates['gpi'][600/dt:1400/dt]))/np.mean(SWADopDepRates['gpi'][100/dt:500/dt])		# (Orig - Final)/Orig
		PDFeatures[i][0] = howmuch




		# New features
		Flags=[]
		Flags.append("Trans")
		ipctx1["ip"] = np.zeros((1,2001))
		scale=1
		TransRates = psGA.calcRates(Flags,delay,A*scale,B*scale,False,ipctx1,ipAmp,iptau=p.params["iptau"])
		if ipAmp == 0:
			temp = dict()
			for x in terms1:
				temp[x] = np.mean(TransRates[x])
			baseLineFR.append(temp) 
		#Add noise to remove the DC peak at zero. SE will be calculated correctly then
		# However adding noise at the input stage disturbs frmation of oscillation

		# GPe mostly dont oscillate - hence contributes to increasing SE
		# To catch damped oscillations	
		#noiseLim = 0.05
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
		PDFeatures[i][2] = np.min(ans)
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
		PDFeatures[i][3] = np.min(ans)
		#PDFeatures[i][3] = np.mean(ans)

		'''
		if se21 < se22:
			PDFeatures[i][3] = se21
			PDFeatures[i][4] = dfreq21
			#maxFreq[i][1] = maxFreq21
			#perPowerMaxFreq[i][1] = perMax21
		else:
			PDFeatures[i][3] = se22
			PDFeatures[i][4] = dfreq22
			#maxFreq[i][1] = maxFreq22
			#perPowerMaxFreq[i][1] = perMax22
		'''	

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
		PDFeatures[i][5] = np.min(ans)
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
		PDFeatures[i][7] = np.min(ans)
		#PDFeatures[i][7] = np.mean(ans)
 
		if i%250==0:
			pickle.dump(PDFeatures,open(pathname1+"PDFeaturesnew_BL_"+str(ipAmp)+"_"+str(i)+".pickle","w"))			
			#pickle.dump(randSamps,open(pathname+"randSampsnew.pickle","w"))
			if ipAmp == 0:
				pickle.dump(AllAs,open(pathname1+"AllAs_BL"+str(ipAmp)+".pickle","w"))
		#	pickle.dump(AllASTPs,open(pathname+"AllASTPs.pickle","w"))
				pickle.dump(AllBs,open(pathname1+"AllBs_BL"+str(ipAmp)+".pickle","w"))

	#		pickle.dump(AllAs,open(pathname+"AllAs"+str(i)+".pickle","w"))			
	#		pickle.dump(AllBs,open(pathname+"AllBs"+str(i)+".pickle","w"))			
			
	#	Supressed.append(howmuch)
	#	Sup_Ind.append(ind)
	pickle.dump(baseLineFR,open(pathname1+"baseLineFR_BL"+str(ipAmp)+".pickle","w"))

	pickle.dump(PDFeatures,open(pathname1+"PDFeaturesnew_BL"+str(ipAmp)+".pickle","w"))
	#pickle.dump(perPowerMaxFreq,open(pathname1+"PercentageInMaxPower_"+str(ipAmp)+".pickle","w"))
	#pickle.dump(maxFreq,open(pathname1+"maxFreq_"+str(ipAmp)+".pickle","w"))
	if ipAmp == 0 or ipAmp == 5: # To check if indeed same As are used for different input values, you can delete one of them afterwrads
		pickle.dump(AllAs,open(pathname1+"AllAs_BL"+str(ipAmp)+".pickle","w"))
	#	pickle.dump(AllASTPs,open(pathname+"AllASTPs.pickle","w"))
		pickle.dump(AllBs,open(pathname1+"AllBs_BL"+str(ipAmp)+".pickle","w"))

