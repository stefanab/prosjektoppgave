#!/usr/bin/env python
import bbcon as bbc # Behavior-based controller

# A subclass of Behavior which details the behavior stopping when a blog is detected
class StopFollowLine(bbc.Behavior):

    def __init__(self,bbcon,sensobs=[],trigger=None,act=True,pri=5):
        self.MAX_SPEED = 1000
        self.num_sensors = 6

        self.times_found_gate = 0
        self.last_value = 0 # Initially assume line was last seen on the left
        self.last_error = 0 # Start error at 0
        bbc.Behavior.__init__(self,bbcon, "stop_line_following", sensobs=sensobs,act=act,pri=pri)

    # Determine if the behavior is currently active or not.  This needs to be subclassed for each behavior.
    def do_activation_test(self): return (not self.bbcon.is_gate_found())
    def do_deactivation_test(self): return self.bbcon.is_gate_found()

    # This is the core method for behavior computation; it needs to be subclassed.
    # It's main jobs are a) read sensors, b) update the behavior's match_degree, c) set the motor requests.
    def sense_and_act(self):
        # We only have on sensor object which is the ReflectanceSensors
        sensob = self.sensobs[0]

        values = sensob.get_value() # Returns a 6 dimensional vector 

        greyCount = 0

        for i in range(len(values)):
            value = values[i]
            if value > 0.5:
                greyCount += 1

        # We've reached a gate (blob of dark material)
        if(greyCount == self.num_sensors):
            self.times_found_gate += 1
        # We haven't reached a gate
        else:
            self.times_found_gate = 0 # Set this back to 0

        # If we have found the gate 4 times in a row, so we set the match degree to be one.
        # The match degree is binary because we either want to stop or we don't want to
        if self.times_found_gate > 3:
            # We update the controller, so it knows the gate has been found, which is used
            # by other behaviors in their do_activation_test()/do_deactivation_test() methods
            self.bbcon.set_gate_found(True) 
            self.set_match_degree(1.0)
        else:
            self.set_match_degree(0.0)

        # We are always requesting that we stop the motors in this behavior
        self.set_motor_requests([0,0])

