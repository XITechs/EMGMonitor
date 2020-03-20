from scipy import signal
from scipy.fft import fftshift
import matplotlib.pyplot as plt
import numpy as np

from os import listdir
from os.path import isfile, join

win_len = 4000
rawSize = 4000
num_win = int(rawSize / win_len)
print('Number of wins: ', num_win)
fs = 4000  # Sampling rate

def prepareFilter(w0, fs):
    b, a = signal.iirnotch(w0, 10)  # 60Hz notch
    d, c = signal.butter(8, 15/(fs/2), 'highpass')
    f, e = signal.butter(8, 120/(fs/2), 'lowpass')
    return b, a, d, c, f, e

def addFilter(b, a, data):
    filtered_data = signal.lfilter(b, a, data)
    return filtered_data

def getRawData():
    binPath = 'rawdata/'
    binNumber = 0
    try:
        binNumber = len([name for name in listdir(binPath) if isfile(join(binPath, name))])
    except FileNotFoundError:
        print("rawdata directory not found.\n")

    print('Find bins: ', binNumber)
    fileNumbers = binNumber

    RAW = []
    f0 = 60  # Frequency to be removed from signal (Hz)
    w0 = f0 / (fs / 2)
    b, a, d, c, f, e = prepareFilter(w0, fs)

    for i in range(fileNumbers):
        binpath = []
        binpath.append(binPath + str(i) + '.bin')
        test_str = "".join(binpath)
        raw = np.fromfile(test_str, dtype=np.float64)

        sub_raw = raw[:fs * num_win]  # transforms raw data into 1 sec windows
        sub = np.array_split(sub_raw, num_win)
        for m in range(num_win):
            inwin = sub[m]
            dataAF = inwin
            #dataAF = addFilter(d, c, dataAF)
            #dataAF = addFilter(b, a, dataAF)
            #dataAF = addFilter(f, e, dataAF)
            #dataAF = addFilter(b, a, dataAF)
            RAW.extend(dataAF)
    return RAW

RawData = np.array(getRawData())
plt.figure()
plt.plot(RawData)

f, t, Sxx = signal.spectrogram(RawData, fs, nperseg=400, noverlap=0)
print(f.shape)
print(t.shape)
print(Sxx.shape)
plt.figure()
plt.pcolormesh(t, f, Sxx)
plt.ylabel('Frequency [Hz]')
plt.xlabel('Time [sec]')
plt.show()