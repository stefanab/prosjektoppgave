import picamera
from time import sleep
import sys
import os, errno
import io
from PIL import Image
import numpy as np
import tflearn


class Detector():

    def __init__(self, camera, convnet):
        self.camera = camera
        self.convnet = convnet
        self.counter = 0

    def save_image(self, image):
        image.save("image_" + str(self.counter) + ".jpeg")
        self.counter += 1




    def detect(self):
        image = camera.get_value()

        prediction = self.convnet.predict(image)
        print(prediction)

        if(prediction[1] == 1):
            print("found class")
            save_image(image)


def __main__():
    convnet  = conv_neural_network_model()
    convnet.load("tflearncnnmug.model")
    camera   = Camera()
    detector = Detector(camera, convnet)
    for i in range(10):
        camera.update()
        detector.detect()
        sleep(3)
