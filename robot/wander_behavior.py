#!/usr/bin/env python
import bbcon as bbc # Behavior-based controller
from random import randint

# A subclass of Behavior which details the behavior stopping when a blog is detected
class Wander(bbc.Behavior):

    def __init__(self, bbcon, sensobs=[], trigger=None, act=True, pri=1):
        self.TURN_SPEED = 350

        bbc.Behavior.__init__(self,bbcon,"wander", sensobs=sensobs,act=act,pri=pri)

    # Determine if the behavior is currently active or not.
    # Wander behavior should always be active. It is the dumbest/simplest behavior
    def do_activation_test(self): return True
    def do_deactivation_test(self): return False

    # This is the core method for behavior computation; it needs to be subclassed.
    # It's main jobs are a) read sensors, b) update the behavior's match_degree, c) set the motor requests.
    def sense_and_act(self):
        # There is no extent to which we want to wander. We just always do
        self.set_match_degree(1)
        m = self.random_motor()
        left_speed = 0
        right_speed = 0
        if m: left_speed = self.random_speed()
        else: right_speed = self.random_speed()

        # We are always requesting random motor speeds for this behavior
        self.set_motor_requests([left_speed, right_speed])

    def random_speed(self):
        return randint(200, self.TURN_SPEED)

    def random_motor(self):
        return randint(0, 1)