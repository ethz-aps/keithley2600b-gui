from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QMessageBox, QGroupBox, QFormLayout, QVBoxLayout, QCheckBox, QComboBox, QHBoxLayout, QLineEdit
from pyqtgraph import PlotWidget, plot
from PyQt5.Qt import QLabel, QPushButton
import pyqtgraph as pg
import threading
import data
from time import sleep

class TabTDDB(QWidget):
	"""
	Design and funcionality of Tab for TDDB-measurements.
	"""
	def __init__(self,k,p,d,c):
		super().__init__()

		self.keithley = k
		self.plot = p
		self.data = d
		self.config = c
		self.tddb = False

		self.v = float(self.config['TDDB']['v'])
		self.period = float(self.config['TDDB']['period'])
		self.sampleTime = float(self.config['TDDB']['sampletime'])
		self.vmax = float(self.config['Keithley']['voltage_compliance'])


		self.vLabel = QLabel('Applied Voltage: ')
		self.periodLabel = QLabel('Period: ')
		self.sampleLabel = QLabel('Sampling Time: ')

		self.vSpinBox = QDoubleSpinBox()
		self.vSpinBox.setMaximum(self.vmax)
		self.vSpinBox.setMinimum(1)
		self.vSpinBox.setValue(self.v)

		self.periodSpinBox = QDoubleSpinBox()
		self.periodSpinBox.setMaximum(10000)
		self.periodSpinBox.setMinimum(1)
		self.periodSpinBox.setValue(self.period)

		self.sampleSpinBox = QDoubleSpinBox()
		self.sampleSpinBox.setMaximum(100)
		self.sampleSpinBox.setMinimum(1)
		self.sampleSpinBox.setValue(self.sampleTime)

		self.deviceLabel = QLabel(self)
		self.deviceLabel.setText('Insert the name of your Device:')
		self.line = QLineEdit(self)

		self.buttonStart = QPushButton("Start",self)
		self.buttonStart.clicked.connect(self.start_click)
		self.buttonStop = QPushButton("Stop",self)
		self.buttonStop.clicked.connect(self.stop_click)

		self.graphWidget= pg.PlotWidget()
		self.graphWidget.setBackground('w')
		self.graphWidget.setTitle("TDDB")
		self.graphWidget.setLabel('left','Current')
		self.graphWidget.setLabel('bottom','Time')
		self.graphWidget.showGrid(x=True, y=True)
		self.data_line = self.graphWidget.plot([],[])

		self.timer = QtCore.QTimer()
		self.timer.setInterval(100)
		self.timer.timeout.connect(self.update_plot_data)
		self.timer.start()

		self.createFormGroupbox()
		self.createButtonGroupBox()
		self.createMeasGroupbox()
		self.createDeviceGroupbox()

		self.vbox = QVBoxLayout()
		self.vbox.addWidget(self.FormGroupbox)
		self.vbox.addWidget(self.DeviceGroupbox)
		self.vbox.addWidget	(self.ButtonGroupbox)
		self.vbox.addWidget(self.MeasGroupbox)
		self.setLayout(self.vbox)

	def createDeviceGroupbox(self):
		self.DeviceGroupbox = QGroupBox("Device")
		self.layout = QFormLayout()
		self.layout.addRow(self.deviceLabel, self.line)
		self.DeviceGroupbox.setLayout(self.layout)

	def createMeasGroupbox(self):
		self.MeasGroupbox = QGroupBox("Plot")
		self.layout=QVBoxLayout()
		self.layout.addWidget(self.graphWidget)
		self.MeasGroupbox.setLayout(self.layout)


	def createFormGroupbox(self):
		self.FormGroupbox = QGroupBox("Parameter")
		self.Layout = QFormLayout()
		self.Layout.addRow(self.vLabel, self.vSpinBox)
		self.Layout.addRow(self.periodLabel, self.periodSpinBox)
		self.Layout.addRow(self.sampleLabel, self.sampleSpinBox)
		self.FormGroupbox.setLayout(self.Layout)

	def createButtonGroupBox(self):
		self.ButtonGroupbox = QGroupBox("Measurement")
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.buttonStart)
		self.layout.addWidget(self.buttonStop)
		self.ButtonGroupbox.setLayout(self.layout)

	def update_plot_data(self):
		if(self.data.tddb):
			[self.x,self.y]=self.data.getDataArray()
			self.data_line.setData(self.x,self.y)


	def start_click(self):
		self.data.tddb = True

		self.data_line.clear()
		self.data.clearData()
		self.data.setParamStress(self.vSpinBox.value(),self.periodSpinBox.value()+1,self.sampleSpinBox.value(),self.line.text())

		self.keithley.voltage = self.vSpinBox.value()
		self.keithley.period = self.periodSpinBox.value()+1
		self.keithley.sampling_t = self.sampleSpinBox.value()
		self.keithley.TDDBThread.start()



	def stop_click(self):

		self.keithley.thread.set()
		self.keithley.TDDBThread.join(2)
		self.keithley.TDDBThread=threading.Thread(target=self.keithley.tddb,args=(self.keithley.thread,'test'))
		self.data.closeFile()
