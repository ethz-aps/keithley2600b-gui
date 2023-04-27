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
		self.current_compliance = 0
		self.start_delay = 0
		self.stop_delay = 0

		#self.stop_the_thread = False
		self.abort = False

		#Thread for stress-measurement
		self.pill2kill = threading.Event()
		self.measThread = threading.Thread(target=self.stress, args=(self.pill2kill, 'thread1'))

		#Thread for TDDB
		self.thread = threading.Event()
		self.TDDBThread = threading.Thread(target=self.tddb, args=(self.thread, 'thread2'))

		#Thread for Steady Voltage Breakdown Measurement
		#self.svbd = threading.Event()
		#self.SteadyV_BDThread = threading.Thread(target=self.steadyV_BD, args=(self.svbd, 'thread3'))

		self.address = self.config['Keithley']['address']
		#print(self.address)
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

	def steadyV_BD(self):
		# steady voltage Breakdown meas.
		self.k.smua.source.output = self.k.smua.OUTPUT_ON
		self.k.apply_voltage(self.k.smua, self.voltage)
		self.sampling_t = int(self.sampling_t)
		self.data.openFile()
		end_timer = 0
		count = 1
		meas_break = 100
		count = self.start_delay #How many Meas
		start_time=time.time()
		current_to_big = False
		current_limit = self.current_compliance
		meas_break = self.stop_delay #How many seconds after limit measurement continues
		while True:
			i = self.k.smua.measure.i()
			if count>0: #Measurement does not record the first 5 values because of inaccuries in the measurement system
				count = count -1
				sleep(self.sampling_t-(time.time()-start_time) % self.sampling_t)
				print("time to stabilize Voltage")
				start_time = time.time()
				continue
			tm = time.time() - start_time
			self.data.setDataPoint(tm, i)
			self.data.saveDataPointtoFile(tm, i)
			if self.abort:
				print("pressed Stop")
				break
			if np.abs(i)>=current_limit: #starts timer for end of measurement, because current limit has been reached
				current_to_big = True
			if current_to_big:
				end_timer += 1
			if end_timer > meas_break//self.sampling_t:
				print("last measurement")
				self.abort = True
			sleep(self.sampling_t-(time.time()-start_time) % self.sampling_t)
		self.data.closeFile()
		self.data.steadyV_BD = False
		self.k.apply_voltage(self.k.smua, 0)
		self.k.smua.source.output = self.k.smua.OUTPUT_OFF

	def svbd_baseline(self):
		#voltages, currents = (range(-2000,2010,10),range(-200,201))
		self.k.smua.source.output = self.k.smua.OUTPUT_ON
		voltages,currents = self.k.voltage_sweep_single_smu(self.k.smua, range(-200, 201), 0.05 ,-1, False)
		with open("SteadyV_BD_Baseline.txt","w") as txt_file:
			for i in currents:
				txt_file.write(str(i)+"\n")
