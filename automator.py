from keithley2600 import Keithley2600
from data import Datahandler
from configobj import ConfigObj

PERIOD = 1500
SAMPLING_TIME = 5
DEVICE = "MOSFET 1"


#keithley
config = ConfigObj('config.ini')
address = config['Keithley']['address']
k = Keithley2600(address)


data = Datahandler()
data.tddb = True


k.apply_voltage(k.smua, 0)
k.smua.source.output = k.smua.OUTPUT_ON 

for v in [10, 20, 30]:
	data.setParamTDDB(v, PERIOD, SAMPLING_TIME, DEVICE)
	data.writeHeader()

	print("Voltage {}".format(v))
	print("Opening File..")
	data.openFile()

	k.apply_voltage(k.smua, v)
 
	for t in range(0,PERIOD,SAMPLING_TIME):
		i = k.smua.measure.i()
		print("Point {}/{}, I={}".format(t, PERIOD-1, i))		
		data.setDataPoint(t,i)
		data.saveDataPointtoFile(t,i)

		sleep(SAMPLING_TIME)
	print("Closing File")
	data.closeFile()



