
from numpy import dot, cumsum, where, array_split, savetxt, fromfile, float64, mean, array,sqrt
from numpy import abs as npabs
from numpy import sum as npsum
from numpy.fft import fft
from os import listdir
from os.path import isfile, join
from scipy.signal import iirnotch, butter, lfilter
from math import floor

def prepareFilter(w0, fs):
    b, a = iirnotch(w0, 10)  # 60Hz notch
    d, c = butter(8, 15/(fs/2), 'highpass')
    f, e = butter(8, 120/(fs/2), 'lowpass')

    return b, a, d, c, f, e

def addFilter(b, a, data):
    filtered_data = lfilter(b, a, data)
    return filtered_data


def meanfreq(x, win_size):
    sz = int(win_size / 2) + 1
    pxx = npabs(fft(x)) ** 2
    ps = pxx[1:sz] * 2e-06
    pwr = sum(ps)
    meanfreq = dot(ps, range(1, sz)) / pwr

    return meanfreq


def medfreq(x, win_size):
    sz = int(win_size / 2) + 1
    pxx = npabs(fft(x)) ** 2
    ps = pxx[1:sz] * 2e-06
    cs = cumsum(ps)
    pwr = sum(ps)
    medfreq = where(cs >= pwr * 0.5)[0][0]

    return medfreq


def rms(x):
    x2 = x*x
    rms = sqrt(npsum(x2)/x.size)

    return rms


def arv(x):
    arv = mean(npabs(x))

    return arv


binPath = 'rawdata/'
binNumber = 0
try:
    binNumber = len([name for name in listdir(binPath) if isfile(join(binPath, name))])
except FileNotFoundError:
    print("rawdata directory not found.\n")

print('Find bins: ', binNumber)

fileNumbers = binNumber
fs = 4000  # Sampling rate
f0 = 60  # Frequency to be removed from signal (Hz)
w0 = f0/(fs/2)
b, a, d, c, f, e = prepareFilter(w0, fs)

win_len = 4000
max_freq = 500
rawSize = 4000
num_win = floor(rawSize / win_len)
print('Number of wins: ', num_win)




MEF = []
MDF = []
ARV = []
RMS = []


for i in range(fileNumbers):
    binpath = []
    binpath.append(binPath + str(i) + '.bin')
    test_str = "".join(binpath)
    raw = fromfile(test_str, dtype=float64)

    sub_raw = raw[:fs * num_win]  # transforms raw data into 1 sec windows
    sub = array_split(sub_raw, num_win)
    for m in range(num_win):
        inwin = sub[m]
        dataAF = inwin
        dataAF = addFilter(d, c, dataAF)
        dataAF = addFilter(b, a, dataAF)
        dataAF = addFilter(f, e, dataAF)
        dataAF = addFilter(b, a, dataAF)

        MEF.append(meanfreq(dataAF, win_len))
        MDF.append(medfreq(dataAF, win_len))
        ARV.append(arv(dataAF))
        RMS.append(rms(dataAF))


savetxt("ARV1.csv", array(ARV))
savetxt("RMS1.csv", array(RMS))
savetxt("MEF1.csv", array(MEF))
savetxt("MDF1.csv", array(MDF))
