import sys
import csv
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication,QComboBox ,QWidget, QLineEdit, QMessageBox, QAction, QMainWindow, QHBoxLayout, QVBoxLayout, QGroupBox, QDialog, QDialogButtonBox, QFormLayout, QMenu, QMenuBar, QSpinBox, QTextEdit, QDoubleSpinBox, QTabWidget, QCheckBox
from PyQt5.Qt import Qt, QLabel, QGridLayout, QPushButton
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
from keithley2600 import Keithley2600
from time import sleep
import pickle
import numpy as np
import threading
import os
from os import listdir
import re
from configobj import ConfigObj
from datetime import datetime

class Datahandler:
	"""
	Handles data from the measurements, and saves in separate file.
	"""

	def __init__(self):
		self.datadirectory = os.getcwd()
		self.runner = 0
		self.X=[]
		self.Y=[]

		#Measurement Parameter
		self.start = []
		self.stop =[]
		self.step=[]
		self.delay =[]
		self.t =[]
		self.const=[]
		

		self.i =[]
		self.v =[]
		self.p =[]
		self.s =[]

		self.device = []


		#Parameters of Baseline-IV
		self.IV_start = []
		self.IV_end = []
		self.IV_step = []
		self.IV_int_time = []
		self.IV_delay = []
		self.IV_Baseline = False

		#Parameters of Baseline-OT
		self.OT_start = []
		self.OT_end = []
		self.OT_step = []
		self.OT_const = []
		self.OT_int_time = []
		self.OT_delay = []
		self.OT_Baseline = False

		#Boolean for Tab-Check
		self.ivLeak = False
		self.output = False
		self.transfer = False
		self.stress = False
		self.tddb = False

	def setDataArray(self, x,y):
		self.X = x
		self.Y = y

	def setDataPoint(self, x,y):
		self.X.append(x)
		self.Y.append(y)

	def getDataArray(self):
		return [self.X,self.Y]

	def clearData(self):
		self.X=[]
		self.Y=[]

	def setParamIVLeak(self,vstart, vstop, step, d, t, dev):
		self.start =  vstart
		self.stop = vstop
		self.step = step
		self.delay = d
		self.t = t
		self.device = dev

	def setParamOT(self,vstart, vstop, step, const, d, t, dev):
		self.start =  vstart
		self.stop = vstop
		self.step = step
		self.const= const
		self.delay = d
		self.t = t
		self.device = dev


	def setParamStress(self,i,p,t,dev):
		self.i = i
		self.p = p
		self.s = t
		self.device = dev

	def setParamTDDB(self,v,p,t,dev):
		self.v = v
		self.p = p
		self.s = t
		self.device = dev

	def setBaselineIV(self,y,s,e,st,t,d):
		pickle.dump(self.Y,open(self.datadirectory + "baseline.pkl",'wb'))
		self.IV_start = s
		self.IV_end = e
		self.IV_step = st
		self.IV_int_time = t
		self.IV_delay = d

	def setBaselineOT(self,y,s,e,st,c,t,d):
		pickle.dump(self.Y,open(self.datadirectory + "baseline.pkl",'wb'))
		self.OT_start = s
		self.OT_end = e
		self.OT_step = st
		self.OT_const = c
		self.OT_int_time = t
		self.OT_delay = d

	def checkBaselineIV(self,s,e,st,t,d):
		if(self.IV_start == s and self.IV_end == e and self.IV_step == st and self.IV_int_time == t and self.IV_delay == d):
			self.IV_Baseline = True
		else:
			self.IV_Baseline = False

	def checkBaselineOT(self,s,e,st,c,t,d):
		if(self.OT_start == s and self.OT_end == e and self.OT_step == st and self.OT_const == c and self.OT_int_time == t and self.OT_delay == d):
			self.OT_Baseline = True
		else:
			self.OT_Baseline = False


	def getBaseline(self):
		return pickle.load(open(self.datadirectory + 'baseline.pkl','rb'))
		
	def writeHeader(self):
		"""
		Type of Keithley, Date, int_t, delay, current, start Time of run, etc.
		"""
		self.now = datetime.now()
		self.time = self.now.strftime("%d/%m/%Y %H:%M:%S")
		self.measStart = ['Measurment Start:' + self.time]

		self.keithley = ['Working with Keithley 2636B']
		self.DUT = ['Device under Test: ' + self.device]

		#actual Dataheader, iv = true if IV
		if(self.ivLeak):
			self.headerList = ['Voltage in [V]','Current in [A]']
			self.measType = ['IV-Leakage']
			self.param = ['Start Voltage: ' + str(self.start)],['Stop Voltage: ' + str(self.stop)],['Voltage Steps: ' + str(self.step)],['Delay: ' + str(self.delay)],['t_int: ' + str(self.t)]
		elif(self.output):
			self.headerList = ['Voltage in [V]','Current in [A]']
			self.measType = ['Output-Function']
			self.param = ['Start Voltage: ' + str(self.start)],['Stop Voltage: ' + str(self.stop)],['Voltage Steps: ' + str(self.step)],['Constant Voltage: ' + str(self.const)],['Delay: ' + str(self.delay)],['t_int: ' + str(self.t)]
		elif(self.transfer):
			self.headerList = ['Voltage in [V]','Current in [A]']
			self.measType = ['Transfer-Function']
			self.param = ['Start Voltage: ' + str(self.start)],['Stop Voltage: ' + str(self.stop)],['Voltage Steps: ' + str(self.step)],['Constant Voltage: ' + str(self.const)],['Delay: ' + str(self.delay)],['t_int: ' + str(self.t)]
		elif (self.stress):
			self.headerList = ['Time in [s]','Voltage in [V]']
			self.measType = ['Stress-Measurement']
			self.param = ['Applied Current: ' + str(self.i)],['Length of Measurement: ' + str(self.p)],['Sampled every ' + str(self.s) + ' seconds']
		elif(self.tddb):
			self.headerList = ['Time in [s]','Current in [A]']
			self.measType = ['TDDB-Measurement']
			self.param = ['Applied Voltage: ' + str(self.v)],['Length of Measurement: ' + str(self.p)],['Sampled every ' + str(self.s) + ' seconds']
	
	def openFile(self):
		self.writeHeader()

		self.dir = os.path.join(self.datadirectory,"Data")
		if not os.path.exists(self.dir):
			os.mkdir(self.dir)

		r = self.getNextRunner()

		self.filename = self.dir + "/meas_%d.csv" %(r)
		self.file=open(self.filename,"w")

		self.writer = csv.writer(self.file)
		self.writer.writerow(self.keithley)
		self.writer.writerow(self.measStart)
		self.writer.writerow(self.measType)
		self.writer.writerows(self.param)
		self.writer.writerow(self.DUT)			
		self.writer.writerow(self.headerList)

		#insert etc Header
		

	def saveArraytoFile(self):
		for value in range(len(self.X)):
			self.writer.writerow([self.X[value],self.Y[value]])

	def saveDataPointtoFile(self,x,y):
		self.writer.writerow([x,y])
		

	def closeFile(self):
		self.file.close()

	def getNumbers(self, f):
		return re.search(r'\d+',f).group(0)

	def getNextRunner(self):
		for filename in os.listdir(self.datadirectory + "/Data"):
			n = int(self.getNumbers(filename))
			if (n > self.runner):
				self.runner = n
		
		return self.runner+1


class Keithley(object):
	"""
	Connects to Keithley and can run measurements.
	"""
	def __init__(self,d,c):

		#Parameters of measurement
		self.data = d
		self.config = c
		self.current = 0
		self.period = 0
		self.sampling_t = 0
		self.voltage = 0

		#Thread for stress-measurement
		self.pill2kill = threading.Event()
		self.measThread = threading.Thread(target=self.stress, args=(self.pill2kill, 'test'))


		#Thread for TDDB
		self.thread = threading.Event()
		self.TDDBThread = threading.Thread(target=self.tddb, args=(self.thread, 'test'))


		self.address = self.config['Keithley']['address']
		self.k = Keithley2600(self.address)
		self.k.smua.source.output = self.k.smua.OUTPUT_ON 
		self.v=[]
		self.t=[]
		

	def sweep(self, start, end, step, int_time, delay):
		#voltage sweep
		self.num = int(((end - start)/step)+1)
		(v_smu, i_smu)=self.k.voltage_sweep_single_smu(self.k.smua, np.linspace(start,end,num=self.num),int_time,delay, pulsed=False)
		self.data.setDataArray(v_smu,i_smu)
		self.k.smua.source.output = self.k.smua.OUTPUT_OFF

	def sweep_const(self, start, end, step, const, int_time, delay):
		#voltage sweep
		self.k.apply_voltage(self.k.smub, const)
		self.num = int(((end - start)/step)+1)
		(v_smu, i_smu)=self.k.voltage_sweep_single_smu(self.k.smua, np.linspace(start,end,num=self.num),int_time,delay, pulsed=False)
		self.data.setDataArray(v_smu,i_smu)
		self.k.smua.source.output = self.k.smua.OUTPUT_OFF
		self.k.smua.source.output = self.k.smub.OUTPUT_OFF


	def stress(self,stop_event,arg):
		#stress
		self.k.apply_current(self.k.smua, self.current)
		self.period = int(self.period)
		self.sampling_t = int(self.sampling_t)
		self.data.openFile()
		for t in range(0,self.period,self.sampling_t):
			v = self.k.smua.measure.v()
			self.data.setDataPoint(t,v)
			self.data.saveDataPointtoFile(t,v)

			if stop_event.wait(0.05):
				self.data.stress=False
				self.k.smua.source.output = self.k.smua.OUTPUT_OFF
				return
			
			sleep(self.sampling_t)
	
		self.data.closeFile()
		self.data.stress = False
		self.k.smua.source.output = self.k.smua.OUTPUT_OFF

		self.pill2kill = threading.Event()
		self.measThread = threading.Thread(target=self.stress, args=(self.pill2kill, 'test'))
		
		return


	def tddb(self,stop_event,arg):
		#stress
		self.k.apply_voltage(self.k.smua, self.voltage)
		self.period = int(self.period)
		self.sampling_t = int(self.sampling_t)
		self.data.openFile()
		for t in range(0,self.period,self.sampling_t):
			i = self.k.smua.measure.i()
			self.data.setDataPoint(t,i)
			self.data.saveDataPointtoFile(t,i)

			if stop_event.wait(0.05):
				self.data.tddb=False
				self.k.smua.source.output = self.k.smua.OUTPUT_OFF
				return
			
			sleep(self.sampling_t)
	
		self.data.closeFile()
		self.data.tddb = False
		self.k.smua.source.output = self.k.smua.OUTPUT_OFF

		self.thread = threading.Event()
		self.TDDBThread = threading.Thread(target=self.tddb, args=(self.thread, 'test'))
		return


class Plot:
	"""
	Preprocesses data for ploting.
	"""
	def __init__(self, d):

		self.data = d

	def prep(self):
		#substract baseline from measurement
		self.base = self.data.getBaseline()
		self.base = np.array(self.base)[0]
		self.data.Y = np.array(self.data.Y)
		self.data.Y = np.subtract(self.data.Y,self.base)



class Window(QDialog):
	"""
	Creates Mainwindow, with two Tabs.
	"""

	def __init__(self,k,p,d,c):
		super(Window, self).__init__()

		self.keithley = k
		self.plot = p
		self.data = d
		self.config = c

		self.setWindowTitle("Bachelor Thesis: TDDB Testing of the Gate Oxide")
		self.setFixedHeight(900)
		vbox = QVBoxLayout()
		tabwidget = QTabWidget()

		tabwidget.addTab(TabIVLeak(self.keithley,self.plot,self.data,self.config),"IV Leakage")
		tabwidget.addTab(TabOT(self.keithley,self.plot,self.data,self.config),"Output and Transfer")
		tabwidget.addTab(TabStress(self.keithley,self.plot,self.data,self.config),"Stress")
		tabwidget.addTab(TabTDDB(self.keithley,self.plot,self.data,self.config),"TDDB")
		tabwidget.addTab(TabBaseline(self.keithley,self.plot,self.data),"Baseline")

		vbox.addWidget(tabwidget)
		self.setLayout(vbox)

		self.show()

class TabBaseline(QWidget):
	def __init__(self,k,p,d):
		super().__init__()

		self.keithley = k
		self.plot = p
		self.data = d

		self.graphWidget= pg.PlotWidget()
		self.graphWidget.setBackground('w')
		self.graphWidget.setTitle("Baseline")
		self.graphWidget.setLabel('left','Current')
		self.graphWidget.setLabel('bottom','Voltage')
		self.graphWidget.showGrid(x=True, y=True)

		self.buttonPlot = QPushButton("Plot",self)
		self.buttonPlot.clicked.connect(self.on_click)

		self.createPlotGroupbox()

		self.vbox =QVBoxLayout()
		self.vbox.addWidget(self.PlotGroupbox)
		self.setLayout(self.vbox)

	def on_click(self):
		self.base = self.data.getBaseline()
		#self.base = np.array(self.base)[0]
		self.graphWidget.clear()
		self.graphWidget.plot(self.data.X,self.base)

	def createPlotGroupbox(self):
		self.PlotGroupbox=QGroupBox("Baseline")
		self.layout=QVBoxLayout()
		self.layout.addWidget(self.graphWidget)
		self.layout.addWidget(self.buttonPlot)
		self.PlotGroupbox.setLayout(self.layout)


class TabIVLeak (QWidget):
	"""
	Design and funcionality of Tab for IV Measurements.
	"""
	def __init__(self,k,p,d,c):
		super().__init__()

		self.keithley = k
		self.plot = p
		self.data = d
		self.config = c

		self.vstart = float(self.config['IV-Measurement']['vstart'])
		self.vstop = float(self.config['IV-Measurement']['vstop'])
		self.step = float(self.config['IV-Measurement']['step_size'])
		self.delay = float(self.config['IV-Measurement']['delay'])
		self.tint = float(self.config['IV-Measurement']['t_int'])

		self.vStartLabel = QLabel('Start Voltage: ')
		self.vStopLabel = QLabel('Stop Voltage: ')
		self.vStepLabel = QLabel('dV: ')
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
		self.graphWidget.setLogMode(x=False, y=True)
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

		self.vbox = QVBoxLayout()
		self.vbox.addWidget(self.FormGroupbox)
		self.vbox.addWidget(self.DeviceGroupbox)
		self.vbox.addWidget(self.MeasGroupbox)
		self.setLayout(self.vbox)

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
		self.data.setParamIVLeak(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStopSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value(),self.line.text())
		self.keithley.sweep(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
		self.plot.prep()
		self.data.openFile()
		self.data.saveArraytoFile()
		self.graphWidget.plot(self.data.X,self.data.Y)
		self.data.closeFile()
		self.data.ivLeak = False

	def on_click(self):
		self.data.ivLeak= True
		self.graphWidget.clear()
		if (self.cbBase.isChecked() == False):
			self.data.checkBaselineIV(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
			if(self.data.IV_Baseline):
				self.data.setParamIVLeak(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value(),self.line.text())
				self.keithley.sweep(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
				self.plot.prep()
				self.data.openFile()
				self.data.saveArraytoFile()
				self.graphWidget.plot(self.data.X,self.data.Y)
				self.data.closeFile()
				self.data.ivLeak = False
			else:
				y = self.popUpError.exec_()

		else:
			#Baseline measurement
			self.keithley.sweep(self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
			self.data.setBaselineIV(self.data.Y,self.vStartSpinBox.value(), (self.vStopSpinBox.value()), self.vStepSpinBox.value(),self.tSpinBox.value(),self.delaySpinBox.value())
			x = self.popUp.exec_()	


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


if __name__ == '__main__':
	config = ConfigObj('config.ini')
	data = Datahandler()
	keithley = Keithley(data,config)
	plot =  Plot(data)
	app = QApplication(sys.argv)
	ex = Window(keithley,plot,data,config)
	sys.exit(app.exec_())