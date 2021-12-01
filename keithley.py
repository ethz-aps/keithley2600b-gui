from keithley2600 import Keithley2600
from time import sleep
import threading
import numpy as np


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
		self.v=[]
		self.t=[]
		

	def sweep(self, start, end, step, int_time, delay):
		#voltage sweep
		self.k.smua.source.output = self.k.smua.OUTPUT_ON 
		self.num = int(((end - start)/step)+1)
		(v_smu, i_smu)=self.k.voltage_sweep_single_smu(self.k.smua, np.linspace(start,end,num=self.num),int_time,delay, pulsed=False)
		self.data.setDataArray(v_smu,i_smu)
		self.k.smua.source.output = self.k.smua.OUTPUT_OFF

	def sweep_const(self, start, end, step, const, int_time, delay):
		#voltage sweep
		self.k.smua.source.output = self.k.smua.OUTPUT_ON 
		self.k.apply_voltage(self.k.smub, const)
		self.num = int(((end - start)/step)+1)
		(v_smu, i_smu)=self.k.voltage_sweep_single_smu(self.k.smua, np.linspace(start,end,num=self.num),int_time,delay, pulsed=False)
		self.data.setDataArray(v_smu,i_smu)
		self.k.smua.source.output = self.k.smua.OUTPUT_OFF
		self.k.smua.source.output = self.k.smub.OUTPUT_OFF


	def stress(self,stop_event,arg):
		#stress
		self.k.smua.source.output = self.k.smua.OUTPUT_ON 
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
		self.k.smua.source.output = self.k.smua.OUTPUT_ON 
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
