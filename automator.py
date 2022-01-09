#from keithley2600 import Keithley2600
from data import Datahandler
from configobj import ConfigObj
from time import sleep
import pyvisa as visa

PERIOD = 10
SAMPLING_TIME = 2
DEVICE = "SCT3080KL"




#keithley
config = ConfigObj('config.ini')
address = config['Keithley']['address']
rm = visa.ResourceManager()
kl = rm.open_resource(address)
kl.timeout = 20000


def measureI():
	kl.write("currenta, voltagea = smua.measure.iv()")
	sleep(1)
	current = kl.query("print(currenta)")
	return float(current)


data = Datahandler()
data.tddb = True



kl.write("smua.source.levelv=0")
sleep(0.2)
kl.write("smua.source.output=smua.OUTPUT_ON")

for v in [1,2,3]:
	
	data.setParamTDDB(v, PERIOD, SAMPLING_TIME, DEVICE)
	data.writeHeader()

	print(data.v)

	print("Voltage {}".format(v))
	print("Opening File..")
	data.openFile()

	kl.write("smua.source.levelv={}".format(v))
 
	for t in range(0,PERIOD,SAMPLING_TIME):
		i = measureI()
		#i = k.smua.measure.i()
		print("Point {}/{}, I={}".format(t, PERIOD-1, i))		
		data.setDataPoint(t,i)
		data.saveDataPointtoFile(t,i)

		sleep(SAMPLING_TIME-1)
	print("Closing File")
	data.closeFile()

	sleep(10)


kl.write("smua.source.levelv=0")
kl.write("smua.source.output=smua.OUTPUT_OFF")
