from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QMessageBox, QGroupBox, QFormLayout, QVBoxLayout, QCheckBox, QComboBox, QHBoxLayout, QLineEdit
from pyqtgraph import PlotWidget, plot
from PyQt5.Qt import QLabel, QPushButton
import pyqtgraph as pg
import threading

class TabStress(QWidget):
	"""
	Design and funcionality of Tab for stressing-measurements.
	"""
	def __init__(self,k,p,d,c):
		super().__init__()

		self.keithley = k
		self.plot = p
		self.data = d
		self.config = c

		self.i = float(self.config['Stress-Measurement']['i'])
		self.period = float(self.config['Stress-Measurement']['period'])
		self.sampleTime = float(self.config['Stress-Measurement']['sampletime'])
		self.imax = float(self.config['Keithley']['current_compliance'])


		self.iLabel = QLabel('Applied Current: ')
		self.periodLabel = QLabel('Period: ')
		self.sampleLabel = QLabel('Sampling Time: ')

		self.iSpinBox = QDoubleSpinBox()
		self.iSpinBox.setMaximum(self.imax)
		self.iSpinBox.setMinimum(1e-6)
		self.iSpinBox.setValue(self.i)
		self.iSpinBox.setDecimals(6)
		self.iSpinBox.setSingleStep(1e-6)

		self.periodSpinBox = QDoubleSpinBox()
		self.periodSpinBox.setMaximum(2000)
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
		self.graphWidget.setTitle("Stress-Test")
		self.graphWidget.setLabel('left','Voltage')
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
		self.Layout.addRow(self.iLabel, self.iSpinBox)
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
		if(self.data.stress):
			[self.x,self.y]=self.data.getDataArray()
			self.data_line.setData(self.x,self.y)


	def start_click(self):
		self.data.stress = True
		self.data_line.clear()
		self.data.clearData()
		self.data.setParamStress(self.iSpinBox.value(),self.periodSpinBox.value()+1,self.sampleSpinBox.value(),self.line.text())

		self.keithley.current = self.iSpinBox.value()
		self.keithley.period = self.periodSpinBox.value()+1
		self.keithley.sampling_t = self.sampleSpinBox.value()
		self.keithley.pill2kill.clear()
		self.keithley.measThread.start()



	def stop_click(self):

		self.keithley.pill2kill.set()
		self.keithley.measThread.join(2)
		self.keithley.measThread=threading.Thread(target=self.keithley.stress,args=(self.keithley.pill2kill,'test'))
		self.data.closeFile()


