import csv
import pickle
from datetime import datetime
import threading
import os
from os import listdir
import re
from datetime import datetime


class Datahandler:
	"""
	Handles data from the measurements, and saves in separate file.
	"""

	def __init__(self):

		#self.datadirectory = "/home/jhora/Desktop/Bachelor/"
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

	def saveArraytoFile(self):
		for value in range(len(self.X)):
			self.writer.writerow([self.X[value],self.Y[value]])

	def saveDataPointtoFile(self,x,y):
		self.writer.writerow([x,y])
		

	def closeFile(self):
		self.file.close()

	def getNumbers(self, f):
		try: 
			return re.search(r'\d+',f).group(0)
		except AttributeError:
			pass
			return

	def getNextRunner(self):
		for filename in os.listdir(self.datadirectory + "/Data"):
			n = int(self.getNumbers(filename))
			if (n > self.runner):
				self.runner = n
		
		return self.runner+1

