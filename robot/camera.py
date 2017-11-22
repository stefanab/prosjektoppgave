import os, io
from PIL import Image
import picamera as picam
import numpy as np
from time import sleep

class Camera():

    def __init__(self, width, height,save=True, img_rot=0):
        camera     = picam.PiCamera(resolution=(width, height), framerate=30)
        camera.iso = 200
        
        
        camera.shutter_speed= camera.exposure_speed
        sleep(2)
        camera.exposure_mode ='off'
        g = camera.awb_gains
        camera.awb_mode = 'off'
        camera.awb_gains = g
        
        
        
        self.camera = camera
        print(self.camera)
        self.save = save
        self.count = 0
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
        if(self.save):
            im = Image.fromarray(self.value)
            im.save("img" + str(self.count) + ".jpg")
            self.count += 1
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
