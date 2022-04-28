from PyQt5.QtWidgets import QWidget, QDoubleSpinBox, QMessageBox, QGroupBox, QFormLayout, QVBoxLayout, QCheckBox, QComboBox, QLineEdit
from pyqtgraph import PlotWidget, plot
from PyQt5.Qt import QLabel, QPushButton
import pyqtgraph as pg

 class TabOT (QWidget):
	"""
	Design and funcionality of Tab for one voltage sweep and one constant voltage.
	"""
	def __init__(self,k,p,d,c):
		super().__init__()

		self.keithley = k
		self.plot = p
		self.data = d
		self.config = c

		vbox = QVBoxLayout()

		self.typeComboBox = QComboBox()
		self.typeComboBox.addItem('Output-Function')
		self.typeComboBox.addItem('Transfer-Function')
		self.typeLabel= QLabel('Choose the type of measurement')

		self.vstart = float(self.config['IV-Measurement']['vstart'])
		self.vstop = float(self.config['IV-Measurement']['vstop'])
		self.step = float(self.config['IV-Measurement']['step_size'])
		self.vconst = float(self.config['IV-Measurement']['const'])
		self.delay = float(self.config['IV-Measurement']['delay'])
		self.tint = float(self.config['IV-Measurement']['t_int'])

		self.vStartLabel = QLabel('Start Voltage: ')
		self.vStopLabel = QLabel('Stop Voltage: ')
		self.vStepLabel = QLabel('dV: ')
		self.vConstLabel = QLabel('Const Voltage: ')
		self.delayLabel = QLabel('Delay: ')
		self.tLabel = QLabel('Int Time: ')

		self.vStartSpinBox = QDoubleSpinBox()
		self.vStartSpinBox.setMaximum(20)
		self.vStartSpinBox.setMinimum(-5)
		self.vStartSpinBox.setValue(self.vstart)

		self.vStopSpinBox = QDoubleSpinBox()
		self.vStopSpinBox.setMaximum(50)
		self.vStopSpinBox.setMinimum(20)
		self.vStopSpinBox.setValue(self.vstop)

		self.vStepSpinBox = QDoubleSpinBox()
		self.vStepSpinBox.setMaximum(1)
		self.vStepSpinBox.setMinimum(0.05)
		self.vStepSpinBox.setSingleStep(0.1)
		self.vStepSpinBox.setValue(self.step)

		self.vConstSpinBox = QDoubleSpinBox()
		self.vConstSpinBox.setMaximum(200e-3)
		self.vConstSpinBox.setMinimum(10e-3)
		self.vConstSpinBox.setSingleStep(10e-3)
		self.vConstSpinBox.setValue(self.vconst)

		self.delaySpinBox = QDoubleSpinBox()
		self.delaySpinBox.setMaximum(5)
		self.delaySpinBox.setMinimum(-1)
		self.delaySpinBox.setValue(self.delay)

		self.tSpinBox = QDoubleSpinBox()
		self.tSpinBox.setMaximum(0.1)
		self.tSpinBox.setMinimum(0.0001)
		self.tSpinBox.setDecimals(4)
		self.tSpinBox.setSingleStep(0.0001)
		self.tSpinBox.setValue(self.tint)

		self.deviceLabel = QLabel(self)
		self.deviceLabel.setText('Insert the name of your Device:')
		self.line = QLineEdit(self)

		self.graphWidget= pg.PlotWidget()
		self.graphWidget.setBackground('w')
		self.graphWidget.setTitle("IV-Curve")
		self.graphWidget.setLabel('left','Current')
		self.graphWidget.setLabel('bottom','Voltage')
		self.graphWidget.showGrid(x=True, y=True)

		self.cbBase = QCheckBox("Perform Baseline Measurement",self)
		self.cbBase.setChecked(True)

		self.buttonMeasure = QPushButton("Measure",self)
		self.buttonMeasure.clicked.connect(self.on_click)

		self.popUp = QMessageBox()
		self.popUp.setWindowTitle("Baseline Measurement complete")
		self.popUp.setText("The Baseline Measurement has been completed. Please insert the Transistor!")
		self.popUp.setIcon(QMessageBox.Information)
		self.popUp.buttonClicked.connect(self.popup_clicked)

		self.popUpError = QMessageBox()
		self.popUpError.setWindowTitle("Warning")
		self.popUpError.setText("Parameters of the Baseline Measurement are not the same as for your current Measurement. Please make a new Baseline Measurement!")
		self.popUpError.setIcon(QMessageBox.Warning)

		self.createFormGroupbox()
		self.createMeasGroupbox()
		self.createDeviceGroupbox()
		self.createMeasTypeGroupbox()

		self.vbox = QVBoxLayout()
		self.vbox.addWidget(self.MeasTypeGroupbox)
		self.vbox.addWidget(self.FormGroupbox)
		self.vbox.addWidget(self.DeviceGroupbox)
		self.vbox.addWidget(self.MeasGroupbox)
		self.setLayout(self.vbox)

	def createMeasTypeGroupbox(self):
		self.MeasTypeGroupbox = QGroupBox("Measurement Type")
		self.layout=QFormLayout()
		self.layout.addRow(self.typeLabel, self.typeComboBox)
		self.MeasTypeGroupbox.setLayout(self.layout)

	def createDeviceGroupbox(self):
		self.DeviceGroupbox = QGroupBox("Device")
		self.layout = QFormLayout()
		self.layout.addRow(self.deviceLabel, self.line)
		self.DeviceGroupbox.setLayout(self.layout)

	def createFormGroupbox(self):
		self.FormGroupbox = QGroupBox("Parameter")
		self.layout = QFormLayout()
		self.layout.addRow(self.vStartLabel, self.vStartSpinBox)
		self.layout.addRow(self.vStopLabel, self.vStopSpinBox)
		self.layout.addRow(self.vStepLabel, self.vStepSpinBox)
		self.layout.addRow(self.vConstLabel, self.vConstSpinBox)
		self.layout.addRow(self.delayLabel, self.delaySpinBox)
		self.layout.addRow(self.tLabel, self.tSpinBox)
		self.FormGroupbox.setLayout(self.layout)

	def createMeasGroupbox(self):
		self.MeasGroupbox=QGroupBox("Plot")
		self.layout=QVBoxLayout()
		self.layout.addWidget(self.graphWidget)
		self.layout.addWidget(self.cbBase)
		self.layout.addWidget(self.buttonMeasure)
		self.MeasGroupbox.setLayout(self.layout)

	def popup_clicked(self):
		self.data.setParamOT(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.vConstSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value(),self.line.text())
		self.keithley.sweep_const(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.vConstSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
		self.plot.prep()
		self.data.openFile()
		self.data.saveArraytoFile()
		self.graphWidget.plot(self.data.X,self.data.Y)
		self.data.closeFile()
		self.data.output = False
		self.data.transfer = False

	def on_click(self):
		if(self.typeComboBox.currentText() == 'Output-Function'):
			self.data.output = True
		else:
			self.data.transfer = True
		self.graphWidget.clear()
		if (self.cbBase.isChecked() == False):
			self.data.checkBaselineOT(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(), self.vConstSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
			if(self.data.OT_Baseline):
				self.data.setParamOT(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(), self.vConstSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value(),self.line.text())
				self.keithley.sweep_const(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.vConstSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
				self.plot.prep()
				self.data.openFile()
				self.data.saveArraytoFile()
				self.graphWidget.plot(self.data.X,self.data.Y)
				self.data.closeFile()
				self.data.output = False
				self.data.transfer = False
			else:
				y = self.popUpError.exec_()

		else:
			#Baseline measurement
			self.keithley.sweep_const(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.vConstSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
			self.data.setBaselineOT(self.data.Y,self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(), self.vConstSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
			x = self.popUp.exec_()
#