# authors:Ahmed gamil
#         Mohammed Alaa
#         Mohammed mansour
#         Anas makled
#
# title: Biosignal viewer
#
# file: main program file (RUN THIS FILE)


from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog
import sys
from gui import Ui_MainWindow
from fpdf import FPDF
import numpy as np
import os
import pathlib
from matplotlib.backends.backend_pdf import PdfPages
from classes import Graph, SignalPlotting, Spectrogram
class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(ApplicationWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.SignalIndex = 0
        self.EndYAxis = 0
        self.StartYAxis = 0
        self.signals = [None, None, None]
        self.tem_Scroll = 0
        self.tem_Scroll_ver = 10
        self.report = PdfPages('report.pdf')

        self.ui.open_Button.clicked.connect(self.load_file)
        self.ui.chanel_zoomIn_Button.clicked.connect(self.zoomIn)
        self.ui.stop_play_Button.clicked.connect(self.play_stop)
        self.ui.chanels_zoomOut_Button.clicked.connect(self.zoomOut)
        self.ui.chanels_resetView_Button.clicked.connect(self.RestZoom)
        self.ui.chanels_horizontalScrollBar.valueChanged.connect(
            lambda: self.MoveHorizontal(self.ui.chanels_horizontalScrollBar.value()))

        self.ui.show_hide_Button.clicked.connect(lambda: self.Show_hide(self.ui.select_sig_comboBox.currentIndex()))

        self.ui.chan_color_comboBox.activated.connect(lambda: self.setColor(self.ui.select_sig_comboBox.currentIndex(),
                                                                            self.ui.chan_color_comboBox.currentText()))

        self.ui.chanels_clear_Button.clicked.connect(
            lambda: self.clear_Channel(self.ui.select_sig_comboBox.currentIndex()))

        self.ui.chanels_verticalScrollBar.valueChanged.connect(
            lambda: self.moveVertical(self.ui.select_sig_comboBox.currentIndex(),
                                      self.ui.chanels_verticalScrollBar.value()))

        Graph.signalTimer.timeout.connect(lambda: self.Animate(self.ui.chan_speed_verticalSlider.value()))
        self.data = [("Signal Name", "Max (mV)", "Min (mV)", "Std (mV)", "Mean (mV)", "Median (mV)")]
        self.ui.actionExport_as_PDF.triggered.connect(self.export_to_pdf)
        self.ui.specto_show_comboBox.activated.connect(self.showSpectrogram)
        self.ui.specto_clear_Button.clicked.connect(
            lambda: self.clear_spectrogram(self.ui.specto_show_comboBox.currentIndex()))
        self.ui.OK_Button.clicked.connect(
            lambda: self.setTitle(self.ui.select_sig_comboBox.currentIndex(), self.ui.lineEdit.text(),
                                  self.ui.lineEdit))

    def load_file(self):
        try:
            if self.SignalIndex != 3 and self.signals[self.SignalIndex] is None:
                files_name = QFileDialog.getOpenFileName(self, 'Open only txt or CSV or xls', os.getenv('HOME'),
                                                         "(*.csv *.txt *.xls)")
                path = files_name[0]
                Signal_Name = path.split('/')[-1].split(".")[0]
                if pathlib.Path(path).suffix == ".txt":
                    data = np.genfromtxt(path, delimiter=',')
                    XAxis = data[:, 0]
                    YAxis = data[:, 1]
                    XAxis = list(XAxis[:])
                    YAxis = list(YAxis[:])
                    self.signals[self.SignalIndex] = SignalPlotting(XAxis, YAxis, self.SignalIndex, Signal_Name)
                elif pathlib.Path(path).suffix == ".csv":
                    data = np.genfromtxt(path, delimiter=' ')
                    XAxis = data[:, 0]
                    YAxis = data[:, 1]
                    XAxis = list(XAxis[:])
                    YAxis = list(YAxis[:])
                    self.signals[self.SignalIndex] = SignalPlotting(XAxis, YAxis, self.SignalIndex, Signal_Name)
                elif pathlib.Path(path).suffix == ".xls":
                    data = np.genfromtxt(path, delimiter=',')
                    XAxis = data[:, 0]
                    YAxis = data[:, 1]
                    XAxis = list(XAxis[:])
                    YAxis = list(YAxis[:])
                    self.signals[self.SignalIndex] = SignalPlotting(XAxis, YAxis, self.SignalIndex, Signal_Name)
                Graph.signalTimer.start()
                self.ui.select_sig_comboBox.setItemText(self.SignalIndex, "{} signal".format(Signal_Name))
                self.ui.specto_show_comboBox.setItemText(self.SignalIndex, "{} signal".format(Signal_Name))
                self.data.append(self.signals[self.SignalIndex].getStatistic_info())
                self.SignalIndex += 1
        except:
            pass
    def export_to_pdf(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Times", size=10)
        line_height = pdf.font_size * 2.5
        col_width = pdf.epw / 6  # distribute content evenly
        for row in self.data:
            for datum in row:
                pdf.multi_cell(col_width, line_height, datum, border=1, ln=3, max_line_height=pdf.font_size)
            pdf.ln(line_height)
        pdf.output('try.pdf')
        self.savefigures()

    def moveVertical(self, ChannelIndex, ScrollBarValue):
        try:
            if ScrollBarValue - self.tem_Scroll_ver > 0:
                self.StartYAxis = -1 * self.signals[ChannelIndex].zoomFactor - 0.01 * (ScrollBarValue - 50)
                self.EndYAxis = self.signals[ChannelIndex].zoomFactor - 0.01 * (ScrollBarValue - 50)
                Graph.channelGraph.setYRange(self.StartYAxis, self.EndYAxis)
            else:
                self.StartYAxis += 0.01
                self.EndYAxis += 0.01
                Graph.channelGraph.setYRange(self.StartYAxis, self.EndYAxis)
            self.tem_Scroll_ver = ScrollBarValue
        except:
            pass

    def clear_spectrogram(self, signalIndex):
        SignalPlotting.clear_spectrogram(self.signals[signalIndex])

    def clear_Channel(self, ChannelIndex):
        self.signals[ChannelIndex] = None
        self.ui.select_sig_comboBox.setItemText(ChannelIndex, "")
        self.ui.specto_show_comboBox.setItemText(ChannelIndex, "")

        self.SignalIndex = ChannelIndex

    def play_stop(self):
        try:
            if self.ui.stop_play_Button.text() == "stop":
                Graph.signalTimer.stop()
                self.ui.stop_play_Button.setText("play")
                self.ui.stop_play_Button.setIcon(QtGui.QIcon(QtGui.QPixmap("../icons/play.png")))

            else:
                Graph.signalTimer.start()
                self.ui.stop_play_Button.setText("stop")
                self.ui.stop_play_Button.setIcon(QtGui.QIcon(QtGui.QPixmap("../icons/pause.png")))

        except:
            pass

    def setTitle(self, channelIndex, *args):
        try:

            self.signals[channelIndex].Name = args[0]
            self.signals[channelIndex].plot()
            args[1].clear()

        except:
            pass

    def Show_hide(self, ChannelIndex):
        try:
            if self.ui.show_hide_Button.text() == "Show":
                if self.signals[ChannelIndex].Ishiden:
                    self.signals[ChannelIndex].plot()
                    self.signals[ChannelIndex].Ishiden = False
                    self.ui.show_hide_Button.setText("Hide")
                    self.ui.show_hide_Button.setIcon(QtGui.QIcon(QtGui.QPixmap("../icons/hideicon.jpg")))

            else:
                self.signals[ChannelIndex].resetcolor("black")
                self.signals[ChannelIndex].plot()
                self.signals[ChannelIndex].resetcolor(self.signals[ChannelIndex].tem_Color)
                self.ui.show_hide_Button.setText("Show")
                self.ui.show_hide_Button.setIcon(QtGui.QIcon(QtGui.QPixmap("../icons/dshowicon.png")))



        except:
            pass

    def MoveHorizontal(self, ScrollBarValue):
        try:
            if ScrollBarValue - self.tem_Scroll > 0:
                self.Animate(ScrollBarValue - self.tem_Scroll)
            else:
                self.Animate(ScrollBarValue - self.tem_Scroll)
            self.tem_Scroll = ScrollBarValue


        except:
            pass

    def hide(self, ChannelIndex):
        try:
            self.signals[ChannelIndex].resetcolor("black")
            self.signals[ChannelIndex].plot()
            self.signals[ChannelIndex].resetcolor(self.signals[ChannelIndex].tem_Color)
        except:
            pass

    def setColor(self, ChannelIndex, NewColor):
        try:
            if not self.signals[ChannelIndex].Ishiden:
                self.signals[ChannelIndex].resetcolor(NewColor)
                self.signals[ChannelIndex].plot()
            else:
                self.signals[ChannelIndex].resetcolor(NewColor)
        except:
            pass

    def showSpectrogram(self):
        try:
            if self.ui.specto_show_comboBox.currentIndex() == 0:
                if not Spectrogram.spectrogramIsFree():
                    SignalPlotting.clear_spectrogram(SignalPlotting.deleted_signal)

                SignalPlotting.plotSpectrogram(self.signals[0])

            elif self.ui.specto_show_comboBox.currentIndex() == 1:
                if not Spectrogram.spectrogramIsFree():
                    SignalPlotting.clear_spectrogram(SignalPlotting.deleted_signal)

                SignalPlotting.plotSpectrogram(self.signals[1])

            elif self.ui.specto_show_comboBox.currentIndex() == 2:
                if not Spectrogram.spectrogramIsFree():
                    SignalPlotting.clear_spectrogram(SignalPlotting.deleted_signal)

                SignalPlotting.plotSpectrogram(self.signals[2])

        except:
            pass

    def zoomIn(self):
        try:
            if self.signals[0] is not None:
                self.signals[0].zoomIn(True)
                self.self.signals[1].zoomIn()
                self.self.signals[2].zoomIn()

            if self.signals[0] is None:
                self.signals[1].zoomIn(True)
                self.signals[2].zoomIn()
            elif self.signals[1] is None:
                self.signals[2].zoomIn(True)
        except:
            pass

    def RestZoom(self):
        try:
            if self.signals[0] is not None:
                self.signals[0].RestZoom(True)
                self.self.signals[1].RestZoom()
                self.self.signals[2].RestZoom()

            if self.signals[0] is None:
                self.signals[1].RestZoom(True)
                self.signals[2].RestZoom()
            elif self.signals[1] is None:
                self.signals[2].RestZoom(True)
        except:
            pass

    def zoomOut(self):
        try:
            if self.signals[0] is not None:
                self.signals[0].zoomOut(True)
                self.self.signals[1].zoomOut()
                self.self.signals[2].zoomOut()

            if self.signals[0] is None:
                self.signals[1].zoomOut(True)
                self.signals[2].zoomOut()
            elif self.signals[1] is None:
                self.signals[2].zoomOut(True)
        except:
            pass

    def Animate(self, Speed):
        try:
            if self.signals[0] is not None:
                self.signals[0].resetGraph(Speed, True)
                self.self.signals[1].resetGraph(Speed)
                self.self.signals[2].resetGraph(Speed)
            if self.signals[0] is None:
                self.signals[1].resetGraph(Speed, True)
                self.signals[2].resetGraph(Speed)
            elif self.signals[1] is None:
                self.signals[2].resetGraph(Speed, True)
        except:
            pass

    def savefigures(self):
        try:
            for signalIndex in range(0, 3):
                if self.signals[signalIndex] is None:
                    continue
                else:
                    self.report.savefig(self.signals[signalIndex].getFigure())
                    self.report.savefig(self.signals[signalIndex].getSpectrogram())
            self.report.close()
        except:
            pass

# function for launching a QApplication and running the ui and main window
def window():
    app = QApplication(sys.argv)
    win = ApplicationWindow()

    win.show()
    sys.exit(app.exec_())


# main code
if __name__ == "__main__":
    window()
