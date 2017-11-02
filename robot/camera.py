import os
from PIL import Image
import picamera as picam

class Camera():

    def __init__(self, img_width=128, img_height=96, img_rot=0):
		self.camera     = picam.PiCamera(resolution=(img_width,img_height))
        self.value      = None
        self.img_width  = img_width
        self.img_height = img_height
        self.img_rot    = img_rot

    def get_value(self):  return self.value

    def update(self):
        self.sensor_get_value()
        return self.value

    def reset(self):
        self.value = None

    def sensor_get_value(self):
        
        self.value = self.camera.capture()
		print(self.value)
        # Open the image just taken by raspicam
        # Stores the RGB array in the value field
        #self.value = Image.open('image.png').convert('RGB')

