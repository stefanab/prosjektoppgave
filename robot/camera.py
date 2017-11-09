import os, io
from PIL import Image
import picamera as picam
import numpy as np

class Camera():

    def __init__(self, width=128, height=96, img_rot=0):
        self.camera     = picam.PiCamera(resolution=(width, height))
        self.value      = None
        self.width      = width
        self.height     = height
        self.img_rot    = img_rot
    

    def __exit__(self, type, value, traceback):
        self.camera.close()
        print("camera closed")

    def get_value(self):  return self.value

    def update(self):
        self.sensor_get_value()
        return self.value

    def get_value(self):
        return self.value

    def reset(self):
        self.value = None

    def close(self):
        self.camera.close()

    def sensor_get_value(self):
        stream = io.BytesIO()
        self.value = self.camera.capture(stream, format='jpeg')

        stream.seek(0)


        im = np.array(Image.open(stream), dtype=np.uint8)

        self.value = im
        stream.close()
        # Open the image just taken by raspicam
        # Stores the RGB array in the value field
        #self.value = Image.open('image.png').convert('RGB')
