import picamera
from time import sleep
import sys
import os, errno
import io
from PIL import Image
import numpy as np
import tflearn
from neuralnets import conv_neural_network_model
from robot.camera import Camera

class Detector():

    def __init__(self, camera, convnet):
        self.camera = camera
        self.convnet = convnet
        self.counter = 0

    def save_image(self, image, label="pos"):
        image = Image.fromarray(image)
        
        image.save(label +"_image_" + str(self.counter) + ".jpeg")
        self.counter += 1




    def detect(self):
        image = self.camera.get_value()
        print(image.shape)
        prediction = self.convnet.predict(image.reshape([-1, 96, 128, 3]))
        print(prediction)

        if(prediction[0,1] >= .95):
            print("found class")
            self.save_image(image)
        else:
            self.save_image(image, label="neg")


def __main__():
    print("starting detection")
    convnet  = conv_neural_network_model()
    convnet.load("tflearncnnmug.model")
    camera   = Camera()
    detector = Detector(camera, convnet)
    print("done setup")
    for i in range(10):
        print(i) 
        camera.update()
        detector.detect()
        sleep(3)


if __name__ == '__main__':
    __main__()