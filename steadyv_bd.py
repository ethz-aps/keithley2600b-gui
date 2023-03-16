from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QMessageBox, QGroupBox, QFormLayout, QVBoxLayout, QCheckBox, QLineEdit, QComboBox, QHBoxLayout
from pyqtgraph import PlotWidget, plot
from PyQt5.Qt import QLabel, QPushButton
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore
import threading
import data
import keithley
from time import sleep

class SteadyV_BD (QWidget):
    """
    Design & Functionality of Tab for Steady Voltage Breakdown Measurements
    """
    def __init__(self, k, p, d, c):
        super().__init__()

        self.keithley = k
        self.plot = p
        self.data = d
        self.config = c
        self.steadyV_BD = False

        self.v = float(self.config['SteadyV_BD']['v'])
        self.sampleTime = float(self.config['SteadyV_BD']['sampletime'])
        self.vmax = float(self.config['Keithley']['voltage_compliance'])
        self.current_compliance = float(self.config['SteadyV_BD']['current_compliance'])
        self.stop_delay = float(self.config['SteadyV_BD']['stop_delay'])
        self.start_delay = float(self.config['SteadyV_BD']['start_delay'])

        self.vLabel = QLabel('Applied Voltage [V]: ')
        self.sampleLabel = QLabel('Sampling Time [s]: ')
        self.c_complianceLabel = QLabel('Current Compliance [A]: ')
        self.stop_delayLabel = QLabel('Stop Delay [s]: ')
        self.start_delayLabel = QLabel('Start Delay [#sampletime]: ')

        self.vSpinBox = QDoubleSpinBox()
        self.vSpinBox.setMaximum(200)
        self.vSpinBox.setMinimum(-200)
        self.vSpinBox.setDecimals(3)
        self.vSpinBox.setValue(self.v)

        self.sampleSpinBox = QDoubleSpinBox()
        self.sampleSpinBox.setMaximum(1000)
        self.sampleSpinBox.setDecimals(3)
        self.sampleSpinBox.setMinimum(1e-3)
        self.sampleSpinBox.setValue(self.sampleTime)

        self.c_complianceSpinBox = QDoubleSpinBox()
        self.c_complianceSpinBox.setDecimals(6)
        self.c_complianceSpinBox.setSingleStep(0.001)
        self.c_complianceSpinBox.setMaximum(0.1)
        self.c_complianceSpinBox.setMinimum(0)
        self.c_complianceSpinBox.setValue(self.current_compliance)

        self.start_delaySpinBox = QDoubleSpinBox()
        self.start_delaySpinBox.setMaximum(1000)
        self.start_delaySpinBox.setMinimum(0)
        self.start_delaySpinBox.setValue(self.start_delay)

        self.stop_delaySpinBox = QDoubleSpinBox()
        self.stop_delaySpinBox.setMaximum(100000)
        self.stop_delaySpinBox.setMinimum(0)
        self.stop_delaySpinBox.setValue(self.stop_delay)

        # self.cbBase = QCheckBox("Perform Baseline Measurement", self)
        # self.cbBase.setChecked(True)

        self.deviceLabel = QLabel(self)
        self.deviceLabel.setText('Insert the name of your Device:')
        self.line = QLineEdit(self)

        self.buttonStart = QPushButton("Start", self)
        self.buttonStart.clicked.connect(self.start_click)
        self.buttonStop = QPushButton("Stop", self)
        self.buttonStop.clicked.connect(self.stop_click)
        #self.buttonBaseline = QPushButton("Baseline",self)
        #self.buttonBaseline.clicked.connect(self.baseline_click)

        self.popUp_svbd = QMessageBox()
        self.popUp_svbd.setWindowTitle("Baseline Measurement complete")
        self.popUp_svbd.setText("The Baseline Measurement has been completed.")
        self.popUp_svbd.setIcon(QMessageBox.Information)
        self.popUp_svbd.buttonClicked.connect(self.popup_svbd_clicked)

        # self.popUp = QMessageBox()
        # self.popUp.setWindowTitle("Baseline Measurement complete")
        # self.popUp.setText("The Baseline Measurement has been completed. Please insert the Transistor!")
        # self.popUp.setIcon(QMessageBox.Information)
        # self.popUp.buttonClicked.connect(self.popup_clicked)
        #
        # self.popUpError = QMessageBox()
        # self.popUpError.setWindowTitle("Warning")
        # self.popUpError.setText("Parameters of the Baseline Measurement are not the same as for your current Measurement. Please make a new Baseline Measurement!")
        # self.popUpError.setIcon(QMessageBox.Warning)

        self.graphWidget = pg.PlotWidget()
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle("CSV-TDDB")
        self.graphWidget.setLabel('left', 'Current[A]')
        self.graphWidget.setLabel('bottom', 'Time[s]')
        pen = pg.mkPen(color='k', width=1)

        ticks= np.logspace(-12, 0, 10)
        #self.disableSIPrefix
        self.graphWidget.setLogMode(y=True)
        #self.graphWidget.disableAutoRange(axis='y')
        self.graphWidget.enableAutoRange()
        yax = self.graphWidget.getAxis('left')
        yax.enableAutoSIPrefix(enable=False)
        #yax.setTicks([[(v,str(v)) for v in ticks]])
        self.graphWidget.setLogMode(y=True)
        self.graphWidget.showGrid(x=True, y=True)
        self.graphWidget.setMouseEnabled(x=False,y=True)
        self.data_line = self.graphWidget.plot([], [], pen=pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        self.createFormGroupbox()
        self.createButtonGroupBox()
        self.createMeasGroupbox()
        self.createDeviceGroupbox()

        self.vbox = QVBoxLayout()
        self.vbox.addWidget(self.FormGroupbox)
        self.vbox.addWidget(self.DeviceGroupbox)
        self.vbox.addWidget(self.ButtonGroupbox)
        self.vbox.addWidget(self.MeasGroupbox)
        self.setLayout(self.vbox)

    def createDeviceGroupbox(self):
        self.DeviceGroupbox = QGroupBox("Device")
        self.layout = QFormLayout()
        self.layout.addRow(self.deviceLabel, self.line)
        self.DeviceGroupbox.setLayout(self.layout)

    def createMeasGroupbox(self):
        self.MeasGroupbox = QGroupBox("Plot")
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.graphWidget)
        self.MeasGroupbox.setLayout(self.layout)

    def createFormGroupbox(self):
        self.FormGroupbox = QGroupBox("Parameter")
        self.Layout = QFormLayout()
        self.Layout.addRow(self.vLabel, self.vSpinBox)
        self.Layout.addRow(self.sampleLabel, self.sampleSpinBox)
        self.Layout.addRow(self.c_complianceLabel, self.c_complianceSpinBox)
        self.Layout.addRow(self.start_delayLabel, self.start_delaySpinBox)
        self.Layout.addRow(self.stop_delayLabel, self.stop_delaySpinBox)
        self.FormGroupbox.setLayout(self.Layout)

    def createButtonGroupBox(self):
        self.ButtonGroupbox = QGroupBox("Measurement")
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.buttonStart)
        self.layout.addWidget(self.buttonStop)
        #self.layout.addWidget(self.buttonBaseline)
        self.ButtonGroupbox.setLayout(self.layout)

    def update_plot_data(self):
        y=[]
        yax = self.graphWidget.getAxis('left')

        if y:
            maxim = max(y)
            i= -14
            while (10**i<maxim):
                i= i+1
            minim = min(y)
            j=1
            while (10**j>minim):
                j = j-1
            tick = np.logspace(j, i, num = 1000)
            ticks = list(tick)
            #self.graphWidget.setRange(yRange=(minim, maxim))
            #yax.setTicks([[(v, str(v)) for v in ticks]])
        if (self.data.steadyV_BD):
            [x, y] = self.data.getDataArray()
            self.data_line.setData(x, y)


        # def popup_clicked(self):
        #     self.data.setParamSteadyV_BD(self.vSpinBox.value(), self.sampleSpinBox.value(),self.line.text())
        #     self.keithley.voltage = self.vSpinBox.value()
        #     self.sampling_t = self.sampleSpinBox.value()
        #     self.plot.prep()
        #     self.data.openFile()
        #     self.data.saveArraytoFile()
        #     self.graphWidget.plot(self.data.X, self.data.Y)
        #     self.data.closeFile()
        #     self.data.steadyV_bd = False

    def start_click(self):
        self.data.steadyV_BD = True
        self.keithley.abort = False
        self.data_line.clear()
        self.data.clearData()
        self.data.setParamSteadyV_BD(self.vSpinBox.value(), self.sampleSpinBox.value(), self.c_complianceSpinBox.value(),
                               self.start_delaySpinBox.value, self.stop_delaySpinBox.value(), self.line.text())

        self.keithley.voltage = self.vSpinBox.value()
        self.keithley.sampling_t = self.sampleSpinBox.value()
        self.keithley.current_compliance = self.c_complianceSpinBox.value()
        self.keithley.start_delay = self.start_delaySpinBox.value()
        self.keithley.stop_delay = self.stop_delaySpinBox.value()
        global SteadyV_BDThread
        SteadyV_BDThread = threading.Thread(target=self.keithley.steadyV_BD)
        SteadyV_BDThread.start()

    def stop_click(self):
        self.keithley.abort = True
        SteadyV_BDThread.join()
        self.data.closeFile()


    def baseline_click(self):
        self.keithley.svbd_baseline()
        self.popUp_svbd.exec_()

    def popup_svbd_clicked(self):
        pass
