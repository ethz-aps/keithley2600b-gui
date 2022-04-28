from PyQt5.QtWidgets import QGroupBox, QWidget, QVBoxLayout
from PyQt5.Qt import QPushButton
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import data

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

