import os, io
from PIL import Image
import picamera as picam
import numpy as np

class Camera():

    def __init__(self, width=128, height=96, img_rot=0):
	self.camera     = picam.PiCamera(resolution=(width, height))
        self.value      = None
        self.width  = width
        self.height = height
        self.img_rot    = img_rot

    def get_value(self):  return self.value

    def update(self):
        self.sensor_get_value()
        return self.value

    def reset(self):
        self.value = None

    def sensor_get_value(self):
        stream = io.BytesIO()
        self.value = self.camera.capture(stream, format='jpeg')
	print(self.value)
	stream.seek(0)
	
	print(self.value)
	im = np.array(Image.open(stream), dtype=np.uint8)
	print(im)
        # Open the image just taken by raspicam
        # Stores the RGB array in the value field
        #self.value = Image.open('image.png').convert('RGB')

