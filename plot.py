import numpy as np

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