import sys
from configobj import ConfigObj
from PyQt5.QtWidgets import QApplication
from keithley import Keithley
from data import Datahandler
from plot import Plot
from window import Window


if __name__ == '__main__':
	config = ConfigObj('config.ini')
	data = Datahandler()
	keithley = Keithley(data,config)
	plot =  Plot(data)
	app = QApplication(sys.argv)
	ex = Window(keithley,plot,data,config)
	sys.exit(app.exec_())