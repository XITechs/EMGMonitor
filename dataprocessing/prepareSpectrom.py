from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

fs = 4000  # Sampling rate

def applyDynamicRange(newSxx):
    maxSxx = np.max(newSxx)
    newSxx[np.where(newSxx > 0.1 * maxSxx)] = 0.1 * maxSxx
    return newSxx

def cutFrequncy(f, newSxx):
    cut = 15
    f = f[0:cut]
    newSxx = newSxx[0:cut]
    return f, newSxx

def getSpectrom(time):
    binStr = 'rawdata/'+str(time) + '.bin'
    RawData = np.fromfile(binStr, dtype=np.float64)
    f, t, Sxx = signal.spectrogram(RawData, fs, nperseg=400, noverlap=0)
    Sxx = applyDynamicRange(Sxx)
    newf, newSxx = cutFrequncy(f, Sxx)
    return newSxx


plt.figure()
plt.pcolormesh(getSpectrom(30))
plt.ylabel('Frequency [10Hz]')
plt.xlabel('Time [sec]')
plt.show()
