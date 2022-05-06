from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QMessageBox, QGroupBox, QFormLayout, QVBoxLayout, QCheckBox, QLineEdit, QComboBox, QHBoxLayout
from pyqtgraph import PlotWidget, plot
from PyQt5.Qt import QLabel, QPushButton
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtCore
import threading
import data
import keithley



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

        self.vLabel = QLabel('Applied Voltage: ')
        self.sampleLabel = QLabel('Sampling Time: ')

        self.vSpinBox = QDoubleSpinBox()
        self.vSpinBox.setMaximum(200)
        self.vSpinBox.setMinimum(-200)
        self.vSpinBox.setValue(self.v)

        self.sampleSpinBox = QDoubleSpinBox()
        self.sampleSpinBox.setMaximum(100)
        self.sampleSpinBox.setMinimum(1)
        self.sampleSpinBox.setValue(self.sampleTime)

        # self.cbBase = QCheckBox("Perform Baseline Measurement", self)
        # self.cbBase.setChecked(True)

        self.deviceLabel = QLabel(self)
        self.deviceLabel.setText('Insert the name of your Device:')
        self.line = QLineEdit(self)

        self.buttonStart = QPushButton("Start", self)
        self.buttonStart.clicked.connect(self.start_click)
        self.buttonStop = QPushButton("Stop", self)
        self.buttonStop.clicked.connect(self.stop_click)
        self.buttonBaseline = QPushButton("Baseline",self)
        self.buttonBaseline.clicked.connect(self.baseline_click)

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
        self.graphWidget.setTitle("Steady Voltage BD")
        self.graphWidget.setLabel('left', 'Current')
        self.graphWidget.setLabel('bottom', 'Time')

        ticks= np.logspace(0, 9)
        #self.disableSIPrefix
        self.graphWidget.setLogMode(y=True)
        self.graphWidget.setRange(yRange=(1*10**(-12), 9*10**(0)), disableAutoRange=True)
        self.graphWidget.enableAutoRange(axis='x')
        yax = self.graphWidget.getAxis('left')
        yax.setTicks([[(v,str(v)) for v in ticks]])
        self.graphWidget.setLogMode(y=True)
        self.graphWidget.showGrid(x=True, y=True)
        self.data_line = self.graphWidget.plot([], [])

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
        self.FormGroupbox.setLayout(self.Layout)

    def createButtonGroupBox(self):
        self.ButtonGroupbox = QGroupBox("Measurement")
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.buttonStart)
        self.layout.addWidget(self.buttonStop)
        self.layout.addWidget(self.buttonBaseline)
        self.ButtonGroupbox.setLayout(self.layout)

    def update_plot_data(self):
        if (self.data.steadyV_BD):
            [self.x, self.y] = self.data.getDataArray()
            self.data_line.setData(self.x, self.y)
        max = np.max(self.y)
        min = np.min(self.y)
        ticks = np.logpspace(min, max)
        yax.setTicks([[(v, str(v)) for v in ticks]])


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

        self.data_line.clear()
        self.data.clearData()
        self.data.setParamSteadyV_BD(self.vSpinBox.value(), self.sampleSpinBox.value(),
                               self.line.text())

        self.keithley.voltage = self.vSpinBox.value()
        self.keithley.sampling_t = self.sampleSpinBox.value()
        SteadyV_BDThread = threading.Thread(target=self.keithley.steadyV_BD)
        SteadyV_BDThread.start()

    def stop_click(self):
        self.keithley.abort = True
        self.keithley.SteadyV_BDThread.join()
        self.data.closeFile()

    def baseline_click(self):
        self.keithley.svbd_baseline()
        self.popUp_svbd.exec_()

    def popup_svbd_clicked(self):
        pass
