#!/usr/bin/env python

# -*- coding: utf-8 -*-

import serial
import shutil
import os
import sys
import time
from numpy import array, sqrt, mean, abs, zeros, dot, cumsum, where
from numpy.fft import fft

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow

from scipy.signal import iirnotch, butter, lfilter

""" Returns parameters for three filters

Note: iirnotch behaves differently in Python than Matlab
"""
def prepareFilter(fs):
    w0 = 60 / (fs / 2)
    b, a = iirnotch(w0, 5)  # 60Hz notch
    d, c = butter(8, 15/(fs/2), 'highpass')
    f, e = butter(8, 120/(fs/2), 'lowpass')

    return b, a, d, c, f, e

def addFilter(b, a, data):
    filtered_data = lfilter(b, a, data)

    return filtered_data

def rms(x):
    rms = sqrt(mean(x ** 2))

    return rms

def arv(x):
    arv = mean(abs(x))

    return arv

""" Returns mean power frequency of spectrum

Based on intechopen.com's definition
Should be roughly functionally equivalent to matlab version
"""
def meanfreq(x, win_size):
    sz = int(win_size / 2) + 1
    pxx = abs(fft(x)) ** 2
    ps = pxx[1:sz] * 2e-06
    pwr = sum(ps)
    meanfreq = dot(ps, range(1, sz)) / pwr

    return meanfreq

""" Returns median power frequency of spectrum

Calculates a cumulative sum of the spectrum then locates midpoint
Further improvement may be needed
"""
def medfreq(x, win_size):
    sz = int(win_size / 2) + 1
    pxx = abs(fft(x)) ** 2
    ps = pxx[1:sz] * 2e-06
    cs = cumsum(ps)
    pwr = sum(ps)
    medfreq = where(cs >= pwr * 0.5)[0][0]

    return medfreq


def dataProcess(MEF, MDF, ARV, RMS, x):
    ARV.append(arv(x))
    RMS.append(rms(x))
    MEF.append(meanfreq(x, displayDataNumber))
    MDF.append(medfreq(x, displayDataNumber))
    arvCurve.setData(array(ARV))
    rmsCurve.setData(array(RMS))
    mefCurve.setData(array(MEF))
    mdfCurve.setData(array(MDF))
    return ARV, RMS

if __name__ == '__main__':
    baudRate = 9600
    str1 = 'rawdata/'

    voltagePerUnit = 0.0049
    displayDataNumber = 4000
    fs = 4000

    # rmtree throws an error if data directory not extant
    try:
        shutil.rmtree('./rawdata')
    except FileNotFoundError:
        print("Data directory not found.\nCreating new directory...")
    os.mkdir('./rawdata')

    # Checks validity of serial port before taking time to init PyQt
    while True:
        try:
            # Allows for minimal effort by user
            serialPort = "COM" + input("Port: COM")
            print("Trying to open serial port:", serialPort)
            ser = serial.Serial(serialPort, baudRate, timeout=0.5)
            time.sleep(1)
            if ser.inWaiting() == 0:
                raise IOError
        except IOError:
            print("Unable to open serial port:", serialPort)
            # sys.exit()
            continue
        else:
            break

    rawData = ser.readline()
    print(' √ Get connection!')
    rawData = 0

    
    rawDataArray = zeros(displayDataNumber)

    datablockN = 0

    MEF = []
    MDF = []
    ARV = []
    RMS = []

    b, a, d, c, f, e = prepareFilter(fs)

    app = pg.mkQApp()

    if app is None:
        app = QtCore.QCoreApplication(sys.argv)


    win = QMainWindow()
    win.setWindowTitle('X Signal Analysis')

    winPlotWave = QWidget()
    rawDataPlot = pg.PlotWidget()
    rawDataPlot.setMaximumHeight(250)
    rawDataPlot.setXRange(0, displayDataNumber)
    rawDataPlot.setYRange(0, 2)
    rawDataPlot.setTitle('Raw data')
    rawDataPlot.setLabel('left', 'Volt.', units='v')
    rawDataPlot.setLabel('bottom', 'Sample', units='s')
    waveformData = zeros(displayDataNumber)
    waveformCurve = rawDataPlot.plot(waveformData, pen=pg.mkPen('r', width=1))

    arvDataPlot = pg.PlotWidget()
    arvDataPlot.setMaximumHeight(250)
    arvDataPlot.setYRange(0, 2)
    arvDataPlot.setTitle('ARV')
    arvDataPlot.setLabel('left', 'Volt.', units='v')
    arvDataPlot.setLabel('bottom', 'Time', units='s')
    arvData = zeros(1)
    arvCurve = arvDataPlot.plot(arvData, pen=pg.mkPen('r', width=1))

    rmsDataPlot = pg.PlotWidget()
    rmsDataPlot.setMaximumHeight(250)
    rmsDataPlot.setYRange(0, 2)
    rmsDataPlot.setTitle('RMS')
    rmsDataPlot.setLabel('left', 'Volt.', units='v')
    rmsDataPlot.setLabel('bottom', 'Time', units='s')
    rmsData = zeros(1)
    rmsCurve = rmsDataPlot.plot(rmsData, pen=pg.mkPen('r', width=1))

    mefDataPlot = pg.PlotWidget()
    mefDataPlot.setMaximumHeight(250)
    mefDataPlot.setYRange(10, 150)
    mefDataPlot.setTitle('MEF')
    mefDataPlot.setLabel('left', 'Freq.', units='Hz')
    mefDataPlot.setLabel('bottom', 'Time', units='s')
    mefData = zeros(1)
    mefCurve = mefDataPlot.plot(mefData, pen=pg.mkPen('r', width=1))

    mdfDataPlot = pg.PlotWidget()
    mdfDataPlot.setMaximumHeight(250)
    mdfDataPlot.setYRange(10, 150)
    mdfDataPlot.setTitle('MDF')
    mdfDataPlot.setLabel('left', 'Freq.', units='Hz')
    mdfDataPlot.setLabel('bottom', 'Time', units='s')
    mdfData = zeros(1)
    mdfCurve = mdfDataPlot.plot(mdfData, pen=pg.mkPen('r', width=1))

    winPlotLayout = QtGui.QGridLayout()
    winPlotWave.setLayout(winPlotLayout)
    winPlotLayout.addWidget(mefDataPlot, 0, 0, 1, 1)
    winPlotLayout.addWidget(mdfDataPlot, 0, 1, 1, 1)
    winPlotLayout.addWidget(arvDataPlot, 1, 0, 1, 1)
    winPlotLayout.addWidget(rmsDataPlot, 1, 1, 1, 1)
    winPlotLayout.addWidget(rawDataPlot, 2, 0, 1, 2)

    win.setCentralWidget(winPlotWave)


    win.resize(1000, 600)

    desktop = QApplication.desktop()
    movex = (desktop.width() - win.width()) // 2
    movey = (desktop.height() - win.height()) // 2
    win.move(0, 0)

    win.show()

    

    print(' √ Window is ready!')

    


    while True:
        rawDataCount = 0
        time1 = time.time()
        while rawDataCount < displayDataNumber:
            volData = float(rawData) * voltagePerUnit
            rawDataArray[rawDataCount] = volData
            rawData = ser.readline()
            rawDataCount = rawDataCount + 1


        displayData = rawDataArray
        time2 = time.time()

        waveformCurve.setData(displayData)
        app.processEvents()
        time3 = time.time()
        print('Datablock: ', datablockN)
        print('time cost for display:', time3 - time2)
        print('time cost for acquisition:', time2 - time1)
        #time.sleep(1)
        save_path = str1 + str(datablockN) + '.bin'
        datablockN = datablockN + 1
        dataBin = open(save_path, 'wb', buffering=0)
        dataBin.write(displayData)
        dataBin.close()

        dataAF = displayData
        dataAF = addFilter(d, c, dataAF)
        dataAF = addFilter(b, a, dataAF)
        dataAF = addFilter(f, e, dataAF)
        dataAF = addFilter(b, a, dataAF)

        dataProcess(MEF, MDF, ARV, RMS, dataAF)

    ser.close()
