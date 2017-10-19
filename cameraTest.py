import picamera
from time import sleep
import sys
import os, errno
with picamera.PiCamera(resolution=(128,96)) as camera:
    directory = sys.argv[1]
    images = int(sys.argv[2])
    print(camera.resolution)
    
    try:
        original_umask = os.umask(0)
        os.makedirs(directory, 0777)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
    finally:
        os.umask(original_umask)
        
    
    camera.start_preview()
    try:
        for i, filename in enumerate(camera.capture_continuous(os.path.join(directory, 'image{counter:02d}.jpg'))):
            print(filename)
            sleep(.1)
            if(i == images ):
                break
    finally:
        camera.stop_preview()
            
##    for i in range(100):
##        camera.capture('imagefalse%d.jpg' % (i,))
##        sleep(.1)
##        
##    camera.stop_preview()
