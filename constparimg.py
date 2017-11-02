



class constantParametersImage():

	def __init__(self):
		self.setup()
		
	def setup(self):
	    #Images in tensorflow take input as [height, width, channel]
		self.height = 96
		self.width  = 128
		self.color  = True
		self.channels = 3 if self.color else 1
		
class constantParametersNetwork():

	def __init__(self):
		self.setup()
	
	def setup(self):
		self.n_classes     = 2
		self.n_epochs      = 1000
		self.batch_size    = 128
		self.learning_rate = 0.000001