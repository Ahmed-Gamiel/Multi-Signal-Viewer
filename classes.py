from PyQt5 import QtCore
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import matplotlib.pyplot as plt
import numpy as np
import math
import pandas as pd


class Graph(object):
    signalTimer = QtCore.QTimer()
    signalTimer.setInterval(50)
    channelGraph = None

    @classmethod
    def createPlotWidget(cls):
        cls.channelGraph = pg.PlotWidget()

        cls.channelGraph.setBackground('k')
        cls.channelGraph.setYRange(-1, 1, padding=0)
        cls.channelGraph.setXRange(0, 1, padding=0)
        cls.channelGraph.setLabel('left', 'Amplitude(mV)')
        cls.channelGraph.setLabel('bottom', 'time (sec)')
        # cls.channelGraph.setTitle("channel {}".format(str( 1)))
        cls.channelGraph.showGrid(x=True, y=True)

    @classmethod
    def addItem(cls, X_axis, Yaxis, color, Name):
        cls.channelGraph.setYRange(-1, 1, padding=0)
        cls.channelGraph.addLegend(size=(2, 3))
        return cls.channelGraph.plot(X_axis, Yaxis, pen=color, name=Name)

    @classmethod
    def getLastChannel(cls):
        return cls.channelGraph


class Spectrogram(object):
    freeSpectrogram = True

    @classmethod
    def createSpectrogramWindow(cls):
        cls.spectrogramImageItems = pg.ImageItem()
        cls.spectrogramHistItems = pg.HistogramLUTItem()
        pg.setConfigOptions(imageAxisOrder='row-major')

        pg.mkQApp()
        cls.spectrogramsWindows = pg.GraphicsLayoutWidget()
        # A plot area (ViewBox + axes) for displaying the image
        cls.spectrogramPlotItems = cls.spectrogramsWindows.addPlot()
        # Add labels to the axis
        cls.spectrogramPlotItems.setLabel('bottom', "Time", units='sec')
        cls.spectrogramPlotItems.setXRange(0, 12, padding=0)
        cls.spectrogramPlotItems.setYRange(0, 3, padding=0)
        # If you include the units, Pyqtgraph automatically scales the axis and adjusts the SI prefix (in this case kHz)
        cls.spectrogramPlotItems.setLabel('left', "Frequency", units='Hz')
        cls.spectrogramImageItems = pg.ImageItem()
        # Item for displaying image data

        cls.spectrogramPlotItems.addItem(cls.spectrogramImageItems)
        # Add a histogram with which to control the gradient of the image
        cls.spectrogramHistItems = pg.HistogramLUTItem()
        # Link the histogram to the image
        cls.spectrogramHistItems.setImageItem(cls.spectrogramImageItems)

        cls.spectrogramHistItems.gradient.restoreState({'mode': 'rgb', 'ticks': [(0.5, (0, 182, 188, 255)),
                                                                                 (1.0, (246, 111, 0, 255)),
                                                                                 (0.0, (75, 0, 113, 255))]})
        cls.spectrogramHistItems.gradient.saveState()
        # If you don't add the histogram to the window, it stays invisible, but I find it useful.
        cls.spectrogramsWindows.addItem(cls.spectrogramHistItems)
        # Show the window
        cls.spectrogramsWindows.show()



    @classmethod
    def spectrogramIsFree(cls):
        return cls.freeSpectrogram

    @classmethod
    def getSpectrogramWindow(cls):
        return cls.spectrogramsWindows


class SignalPlotting(object):
    deleted_signal = None
    ColorDic = {"red": 'r', "green": 'g', "yellow": 'y', "blue": 'b', "white": 'w', "black": 'k'}
    temColor = ["red", "green", "white"]

    def __init__(self, X_axis, Y_axis, Signal_Index, Signal_Name):
        self.currentColor = self.__class__.temColor[Signal_Index]
        # self.__class__.Ishiden[v] = False
        self.tem_Color = None
        self.time = X_axis
        self.Ishiden = False
        self.amplitude = Y_axis
        # self.SignalIndex = Signal_Index
        self.max = max(self.amplitude)
        self.min = min(self.amplitude)
        self.zoomFactor = 1
        self.startTimeIdx = 0
        self.endTimeIdx = 150
        self.Name = Signal_Name
        self.pen = pg.mkPen(color=self.__class__.ColorDic[self.currentColor])
        # Graph.channelGraph.setTitle("Channel {}".format(str(self.SignalIndex)))
        self.plotItem = Graph.addItem(self.time, self.amplitude, self.pen, self.Name)
        Graph.channelGraph.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx], padding=0)

    def plot(self):

        self.pen = pg.mkPen(color=self.__class__.ColorDic[self.currentColor])
        Graph.channelGraph.removeItem(self.plotItem)
        self.plotItem = Graph.addItem(self.time, self.amplitude, self.pen, self.Name)

        # self.plotitem=Graph.addItem(self.time[self.startTimeIdx:],self.amplitude[self.startTimeIdx:])
        # Graph.channelGraph.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx], padding=0)
        # Graph.channelGraph.setYRange( -1*self.zoomFactor, 1*self.zoomFactor)
        # Graph.channelGraph.plot(self.time[self.startTimeIdx:], self.amplitude[self.startTimeIdx:], pen=self.pen)
        # Graph.channelGraph.setLimits("bottom",self.min)

    # self.__class__.IsFree[self.signalName] = False

    def __del__(self):
        try:
            Graph.channelGraph.removeItem(self.plotItem)
            # self.__class__.IsFree[self.signalName] = True

        except:
            pass

    @classmethod
    def IsEmpty(cls, x):
        return cls.IsFree[x]

    def zoomIn(self, active=False):
        if self.zoomFactor >= 0.3:
            self.zoomFactor = self.zoomFactor - 0.1
            if active:
                self.adjustGraph()

    def zoomOut(self, active=False):
        if self.zoomFactor < 2:
            self.zoomFactor = self.zoomFactor + 0.1
            if active:
                self.adjustGraph()

    def RestZoom(self, active=False):
        self.zoomFactor = 1
        if active:
            self.adjustGraph()

    def adjustGraph(self):
        self.endTimeIdx = int(self.startTimeIdx + (150 * self.zoomFactor))
        Graph.channelGraph.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx], padding=0)
        Graph.channelGraph.setYRange(-1 * self.zoomFactor, 1 * self.zoomFactor)

    def getFigure(self):
        fig = plt.figure(figsize=(10, 5))
        plt.plot(self.time[self.startTimeIdx:self.endTimeIdx], self.amplitude[self.startTimeIdx:self.endTimeIdx])
        plt.xlabel('time (sec)')
        plt.ylabel('amplitude (mv)')
        return fig

    def getStatistic_info(self):
        std = np.std(self.amplitude)
        mean = np.mean(self.amplitude)
        median = np.median(self.amplitude)

        return self.Name.upper()+" signal", str(self.max)[0:5], str(self.min)[0:5], str(std)[0:5], str(mean)[0:5], str(median)[0:5]

    def getSpectrogram(self):
        fs = 1 / (self.time[1] - self.time[0])
        fig = plt.figure(figsize=(10, 5))
        plt.specgram(self.amplitude, Fs=fs)
        plt.xlabel('time (sec)')
        plt.ylabel('frequency (Hz)')
        return fig

    @classmethod
    def plotSpectrogram(cls, diseredsignal):

        fs = 1 / (diseredsignal.time[1] - diseredsignal.time[0])
        diseredsignal.powerSpectrum, _, _, _ = plt.specgram(diseredsignal.amplitude, Fs=fs)
        # for more colormaps: https://matplotlib.org/2.0.2/examples/color/colormaps_reference.html
        # Sxx contains the amplitude for each pixel
        # spectrogram.spectrogramPlotItems.setYRange(0, diseredsignal.amplitude, padding=0)

        Spectrogram.spectrogramImageItems.setImage(diseredsignal.powerSpectrum)
        # diseredsignal.spectrogramPlotItems.setXRange(diseredsignal.time[diseredsignal.startTimeIdx],
        # diseredsignal.time[diseredsignal.endTimeIdx])
        SignalPlotting.initSpectrogram(diseredsignal)
        Spectrogram.freeSpectrogram = False

    @staticmethod
    def initSpectrogram(diseredsignal):
        # Scale the X and Y Axis to time and frequency (standard is pixels)
        Spectrogram.spectrogramImageItems.scale(diseredsignal.time[-1] / np.size(diseredsignal.powerSpectrum, axis=1),
                                                math.pi / np.size(diseredsignal.powerSpectrum, axis=0))
        SignalPlotting.deleted_signal = diseredsignal

    @staticmethod
    def clear_spectrogram(diseredsignal):
        Spectrogram.spectrogramImageItems.scale(np.size(diseredsignal.powerSpectrum, axis=1) / diseredsignal.time[-1],
                                                np.size(diseredsignal.powerSpectrum, axis=0) / math.pi)
        Spectrogram.spectrogramImageItems.clear()

        Spectrogram.freeSpectrogram = True

    @classmethod
    def spectroisfree(cls):
        return cls.freespectro

    def resetGraph(self, speed, move=False):
        self.startTimeIdx = self.startTimeIdx + speed
        self.endTimeIdx = self.endTimeIdx + speed
        if move:
            self.MoveGraph()

    def MoveGraph(self):
        Graph.channelGraph.setXRange(self.time[self.startTimeIdx], self.time[self.endTimeIdx], padding=0)

    def resetcolor(self, newColor):
        try:
            if newColor == "black":
                self.tem_Color = self.currentColor
                self.Ishiden = True
            self.currentColor = newColor
            # self.__class__.temcolor[self.num] = x
        except:
            pass
