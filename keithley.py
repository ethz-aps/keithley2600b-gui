from keithley2600 import Keithley2600
import time
from time import sleep
import threading
import numpy as np
import os
import stress
import tddb
import steadyv_bd


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

		#self.stop_the_thread = False

		#Thread for stress-measurement
		self.pill2kill = threading.Event()
		self.measThread = threading.Thread(target=self.stress, args=(self.pill2kill, 'thread1'))

		#Thread for TDDB
		self.thread = threading.Event()
		self.TDDBThread = threading.Thread(target=self.tddb, args=(self.thread, 'thread2'))

		#Thread for Steady Voltage Breakdown Measurement
		self.svbd = threading.Event()
		self.SteadyV_BDThread = threading.Thread(target=self.steadyV_BD, args=(self.svbd, 'thread3'))

		self.address = self.config['Keithley']['address']
		self.k = Keithley2600(self.address,open_timeout = 1000)
		self.k.smua.source.output = self.k.smua.OUTPUT_ON
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

	def tddb(self, stop_event, arg):

		#tddb
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

	def steadyV_BD(self, stop_event, arg):         #Ignore 5 first
		# steady voltage Breakdown meas.
		self.k.smua.source.output = self.k.smua.OUTPUT_ON
		self.k.apply_voltage(self.k.smua, self.voltage)
		self.sampling_t = int(self.sampling_t)
		self.data.openFile()
		i_prev = 10
		count = 0

		while True:

			i = self.k.smua.measure.i()
			tm = time.time()-start_time
			if count<5: #Measurement does not record the first 5 values because of inaccuries in the measurement system
				count = count + 1
				sleep(self.sampling_t)
				start_time = time.time()
				continue

			self.data.setDataPoint(tm, i)
			self.data.saveDataPointtoFile(tm, i)
			if stop_event.wait(0.1):
				self.data.steadyV_BD = False
				self.k.smua.source.output = self.k.smua.OUTPUT_OFF

				break
			sleep(self.sampling_t)

			if np.abs(i-i_prev) > 10*np.abs(i_prev) or np.abs(i) > 0.1:

				break
			i_prev = i
			tm = tm + self.sampling_t
		self.data.closeFile()
		self.data.steadyV_BD = False
		self.k.smua.source.output = self.k.smua.OUTPUT_OFF

		self.svbd = threading.Event()
		self.SteadyV_BDThread = threading.Thread(target=self.steadyV_BD, args=(self.svbd, 'test3'))
		return
