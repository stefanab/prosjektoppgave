import picamera
from time import sleep
import sys
import os, errno
with picamera.PiCamera(resolution=(128,96), framerate=30) as camera:
   # directory = sys.argv[1]
   # images = int(sys.argv[2])
   # print(camera.resolution)
    
   # try:
   #     original_umask = os.umask(0)
   #     os.makedirs(directory, 0777)
   # except OSError as exception:
   #     if exception.errno != errno.EEXIST:
   #         raise
   # finally:
   #     os.umask(original_umask)
        
    camera.iso = 200
    sleep(2)
    camera.shutter_speed = camera.exposure_speed
    camera.exposure_mode = 'off'
    g = camera.awb_gains
    camera.awb_mode ='off'
    camera.awb_gains = g
    camera.capture("img.jpg")
   # try:
   #     for i, filename in enumerate(camera.capture_continuous(os.path.join(directory, 'image{counter:02d}.jpg'))):
   #         print(filename)
   #         #sleep(.)
   #         if(i == images ):
   #             break
   # finally:
    
    
   camera.close()         
##    for i in range(100):
##        camera.capture('imagefalse%d.jpg' % (i,))
##        sleep(.1)
##        
##    camera.stop_preview()
