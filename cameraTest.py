import picamera
from time import sleep

camera = picamera.PiCamera()

camera.start_preview()
for i in range(100):
    camera.capture('imagefalse%d.jpg' % (i,))
    sleep(.1)
    
camera.stop_preview()