



class constantParametersImage():

	def __init__(self):
		self.setup()
		
	def setup(self):
		self.width  = 128
		self.height = 96
		self.color  = True
		self.channels = 3 if self.color else 1