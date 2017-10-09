from time import sleep
import bbcon as bbc # Behavior-based controller
from camera import Camera
from motors import Motors
from PIL import Image
import random
import sys

# A subclass of Behavior which details the behavior of following a line
class Camera_search(bbc.Behavior):

    def __init__(self,bbcon, sensobs=[],trigger=None,act=False,pri=3):
        bbc.Behavior.__init__(self,bbcon, "camera_search", sensobs=sensobs,act=act,pri=pri)
        self.NORMAL_SPEED = 300
        self.TURN_SPEED = 300
        self.mean_x = 0
        self.mean_y = 0
        self.min_pixels = 40 # If less than 40 red pixels are found, the blob is not in reach
        self.max_pixels = 3000 # if the number of red pixels exceed 4000, we say we have found the blob and terminates
        self.offset_x = 0 # Initially assumes the red object is in front
        # If the centroid of the blob is less then min_offset left or right, it is considered centered
        self.min_offset = 16
        self.blob_in_reach = False # True if the red object is anywhere in the picture taken

    # Determine if the behavior is currently active or not.
    def do_activation_test(self):
        return self.bbcon.is_gate_found()
    def do_deactivation_test(self):
        return not self.bbcon.is_gate_found()

    # This is the core method for behavior computation; it needs to be subclassed.
    # It's main jobs are a) read sensors, b) update the behavior's match_degree, c) set the motor requests.
    def sense_and_act(self):
        # We only have on sensor object which is the ReflectanceSensors
        sensob = self.sensobs[0] # Get the camera sensorobject
        image = sensob.get_value() # Returns a two-dimensional pixel vector
        # If image for some reason not taken, dismiss behaviour
        if image == None:
            self.set_match_degree(0)
            self.set_motor_requests([0, 0])
            return

        # counting x and y to find center
        pix_x = 0
        pix_y = 0

        # number of pixels accumulated
        pix_count = 0

        for x in range(0, sensob.sensor.img_width):
            for y in range(0, sensob.sensor.img_height):
                # get the value of the current pixel
                red, green, blue = image.getpixel((x, y))

                # check if the red intensity is sufficeant. Theese conditions has to be tweeked.
                if red > 120 and red > 1.5*blue and red > 1.5* green:
                    #print (red, green, blue)
                    # add the x and y of the found pixel to the accumulators
                    pix_x += x
                    pix_y += y
                    # increment the accumulated pixels' count
                    pix_count += 1
                    # change the pixel colour to black here
                    image.putpixel((x, y), (0, 0, 0))

        # If the blob is visible in the image
        if pix_count > self.min_pixels:
            self.blob_in_reach = True
            self.calculate_offset(sensob, pix_x, pix_y, pix_count)
            # The program should terminate when you are close enough to the blob
            if pix_count > self.max_pixels:
                print("Blob found, program terminated")
                self.bbcon.set_blob_found(True)
                return
        else: self.blob_in_reach = False
        print("Blob in reach: " + str(self.blob_in_reach))

        return self.set_motors()

    def set_motors(self):
        # What to do when the blob is not visible?
        # One alternative is to rotate for a while and check again.
        # It will never leave camera behaviour this way
        # Another is to let the wander behaviour take over. This is done by
        # changing the match degree to 0 and motor requests to [0, 0]
        if not self.blob_in_reach:
            self.set_match_degree(random.random())
            self.set_motor_requests([-self.TURN_SPEED, self.TURN_SPEED])
            return

        # Turns towards the blob or goes straight forward, depending on the offset
        if abs(self.offset_x) <= self.min_offset:
            self.set_motor_requests([self.NORMAL_SPEED, self.NORMAL_SPEED])
        elif self.offset_x < -self.min_offset:
            self.set_motor_requests([-self.TURN_SPEED, self.TURN_SPEED])
        elif self.offset_x > self.min_offset:
            self.set_motor_requests([self.TURN_SPEED, -self.TURN_SPEED])
        self.set_match_degree(1)

    def calculate_offset(self, sensob, pix_x, pix_y, pix_count):
        print("Pixel count: " + str(pix_count))
        # calculate the mean x and y positions
        self.mean_x = pix_x / pix_count
        self.mean_y = pix_y / pix_count
        # The image is ether left, right or centered. This is given by the offset
        self.offset_x = self.mean_x - sensob.sensor.img_width/2
        print("Offset: " + str(self.offset_x))
