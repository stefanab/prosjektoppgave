



class constantParametersImage():

	def __init__(self):
		self.setup()

	def setup(self):
	    #Images in tensorflow take input as [height, width, channel]
		self.height = 32
		self.width  = 128
		self.color  = True
		self.channels = 3 if self.color else 1

class constantParametersNetwork():

	def __init__(self):
		self.setup()

	def setup(self):
		self.batch         = False
		self.n_classes     = 2
		self.n_epochs      = 1000
		self.batch_size    = 128
		self.l_rate        = 0.00001
		self.has_camera    = True
		self.has_ref       = True
