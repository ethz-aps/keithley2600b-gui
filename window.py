from PyQt5.QtWidgets import QVBoxLayout, QTabWidget, QDialog
from baseline import TabBaseline
from iv import TabIVLeak
from output_transfer import TabOT
from stress import TabStress
from tddb import TabTDDB

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