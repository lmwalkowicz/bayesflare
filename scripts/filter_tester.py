import numpy as np
import matplotlib
import matplotlib.pyplot as pl
from math import log
import matplotlib.cm as cm
import bayesflare as bf
from matplotlib.mlab import find
import sys
import os
from copy import copy


def Chi_sq(no_noise_data, smoothed, sigma):
	res = no_noise_data - smoothed
	return np.sqrt(np.sum(res**2)/(len(no_noise_data)-1.))/sigma
	
tlength = 2893536. #length of time data
tstep = 1765.55929 #time data step
nstd = 1. #noise standard deviation
bglen = 55 #background window length (must be odd) so there is always a bin in the centre
bgorder = 4 #The polynomial order of the fitted background variability
taug = 1800 #Gaussian rise width of injected flare (sec)
taue = 3600 #Exponential decay timescale of injected flare (sec)
noiseest = 'powerspectrum'
kneevalue = 0.00003858
psest = 0.5 #fraction of the spectrum with which to estimate the noise
freq = (1./(4.*86400.))
amp = 4

injamp = 50 #change this (injected flare amplitude)
alpha = 0 #can be None or from 0 to 10 smoothest is 10 (for super smoother)
period=350000

ts = np.arange(0., tlength, tstep, dtype='float64')
flarelc = bf.Lightcurve()
flarelc.clc = nstd*np.random.randn(len(ts)) #clc y data
flarelc.cts = np.copy(ts) #cts time stamp data
flarelc.cadence = 'long'

tmi = flarelc.cts-flarelc.cts[0] #makes time data start at 0
Mfi = bf.Flare(tmi, amp=1.) #creates a Flare object
t0 = tmi[int(len(tmi)/2)] #central time of flare set to middle of time data

pdict = {'t0': t0, 'amp': injamp, 'taugauss': taug, 'tauexp': taue}
injdata = np.copy(Mfi.model(pdict)) #creates a flare in the flare object Mfi, using data pdict, copies this into injdata

flarelc.clc = flarelc.clc + injdata #adds flare model to data

phase = 2.*np.pi*np.random.rand(1)
sinewave = amp*np.sin(2.*np.pi*freq*ts + phase)
flarelc.clc = flarelc.clc + sinewave

tmpcurve = copy(flarelc)
fig, ax = pl.subplots(6)
ax[0].plot(tmpcurve.cts, tmpcurve.clc, 'b')


tmpcurve.detrend(method='savitzkygolay', nbins=bglen, order=bgorder)
ax[1].plot(tmpcurve.cts, tmpcurve.clc,'k')
Chi1 = Chi_sq(injdata, tmpcurve.clc, nstd)

tmpcurve = copy(flarelc)
tmpcurve.detrend(method='highpassfilter', knee=kneevalue)
ax[2].plot(tmpcurve.cts, tmpcurve.clc,'b')
Chi2 = Chi_sq(injdata, tmpcurve.clc, nstd)

tmpcurve = copy(flarelc)
tmpcurve.detrend(method='runningmedian', nbins=bglen)
ax[3].plot(tmpcurve.cts, tmpcurve.clc,'r')
Chi3 = Chi_sq(injdata, tmpcurve.clc, nstd)

tmpcurve = copy(flarelc)
tmpcurve.detrend(method='supersmoother', alpha=alpha)
ax[4].plot(tmpcurve.cts, tmpcurve.clc,'g')
Chi4 = Chi_sq(injdata, tmpcurve.clc, nstd)

tmpcurve = copy(flarelc)
tmpcurve.detrend(method='periodsmoother', alpha=alpha,phase=phase,period=period)
ax[5].plot(tmpcurve.cts, tmpcurve.clc,'g')
Chi5 = Chi_sq(injdata, tmpcurve.clc, nstd)


chi_val = {'savitzkygolay': Chi1, 
			'highpassfilter': Chi2,
			'runningmedian': Chi3,
			'supersmoother': Chi4,
			'periodsmoother': Chi5}

print min(chi_val.items(), key=lambda x: x[1]) 


pl.show()

	
