__author__ = 'keithd'
# Behavior-Based Controller.  See "Behavior-Based Robotics" (Arkin, 1998) for a fantastic overview of these techniques.
import time
import prims1 as p1

# A Behavior-Based Controller, which primarily consists of a list of behavior objects along with an arbitrator for
# deciding which of the behaviors "wins" at each timestep.  The BBCon also has a list of sensory and motor
# objects (sensobs, motobs), some of which are used by each behavior to get at the sensors it needs and to
# affect the relevant motors.  For most applications, each behavior reads SOME sensors but affects ALL motors, which
# are typically just a few wheel drivers.

class BBCon():

    def __init__(self,agent,arb_type='Arbitrator',tdur=0.2,stoch=False):
        self.agent = agent # Agent and controller keep pointers to each other
        self.behaviors = []
        self.active_behaviors = []
        self.sensobs = [] # Sensor objects
        self.motobs = [] # Motor objects
        self.arbitrator = eval(arb_type)(self,stoch=stoch)
        self.timestep_duration = tdur
        self.current_timestep = 0
        # TODO: Should use the variable 'stoch'
        self.stochastic = False

    def add_behavior(self,behav): self.behaviors.append(behav)
    def deactivate_behavior(self,b): self.active_behaviors.remove(b)
    def activate_behavior(self,b): self.active_behaviors.append(b)

    def get_active_behaviors(self):  return self.active_behaviors
    def get_agent(self): return self.agent

    def add_sensob(self,s):  self.sensobs.append(s)
    def add_motob(self,m):   self.motobs.append(m)

    # On each timestep, the controller needs to update sensobs, THEN update the behaviors (which use the sensob
    # values), and THEN call the arbitrator to determine which behavior actually gets to control the motor
    # output.

    def run_one_timestep(self):
        for s in self.sensobs: s.update()
        for b in self.behaviors: b.update()
        action,halt_flag = self.arbitrator.choose_action()
        print('\n Chosen action = ' + str(action))
        if not(halt_flag): self.update_motors(action)
        time.sleep(self.timestep_duration) # Allows current action to run this long
        for s in self.sensobs: s.reset()
        return not(halt_flag)

    def timestep_loop(self):
        while self.run_one_timestep():
            self.current_timestep += 1

    def update_motors(self,values):
        # for m,v in zip(self.motobs,values):
        #     m.set_value(v)
        for m in self.motobs:
            m.set_value(values)

class Arbitrator():

    def __init__(self,bbcon,stoch=False):
        self.bbcon = bbcon
        self.stochastic = stoch

    # This returns both a motor request AND whether or not the process should halt.  Any behavior can
    # request a halt, though it's wise to only allow a few special behaviors to do so, for example those that
    # detect a goal state.

    def choose_action(self):
        behavs = self.bbcon.get_active_behaviors()
        print(p1.merge_strings([b.gen_status_string() for b in self.bbcon.behaviors]) + '\n')
        if behavs:
            best = self.stoch_act_choice(behavs) if self.stochastic else self.best_act_choice(behavs)
            print(best.get_name())
            return [best.get_motor_requests(),best.get_halt_status()]

    def best_act_choice(self,behavs):
        best = behavs[0]
        for b in behavs[1:]:
            if b.get_weight() > best.get_weight():
                best = b
        return best

    # Stochastic choice, biased by the weights of each behavior
    def stoch_act_choice(self,behavs):
        return p1.stochpick(behavs,(lambda b: b.get_weight()))


# **************** BEHAVIOR ********************************
# Each behavior in a BBCon is a modular unit that both analyzes sensor values and produces a desired action.  A behavior
# ONLY has sensobs for the sensors that are relevant to it.  So, for example, a line-following behavior (that
# relies on infrared belly sensors) would not have a sensob for camera input.

class Behavior():

    def __init__(self,bbcon, name,sensobs=[],act=True,pri=1.0):
        self.bbcon = bbcon # Keep pointer to the controller
        self.name = name
        self.sensobs = sensobs # Those that are relevant for the behavior.
        self.motor_requests = []
        self.halt_request = False # If True and this behavior wins out, then controller halts the run.
        self.active = act
        if act: self.activate()
        self.priority = pri # Static measure of the behavior's importance.
        self.match_degree = 0 # Degree to which sensor values are appropriate for executing the behavior.
        self.weight = 0 #  (priority * match_degree) = what the arbitrator uses to rank behaviors

    def is_active(self): return self.active
    def get_weight(self): return self.weight
    def get_motor_requests(self): return self.motor_requests
    def set_motor_requests(self,rlist): self.motor_requests = rlist
    def request_halt(self): self.halt_request = True
    def get_halt_status(self): return self.halt_request
    def set_match_degree(self,fraction): self.match_degree = fraction

    def gen_status_string(self):
        aflag = '*' if self.active else ''
        return str(self.weight) + aflag

    # Sensobs are marked to keep track of how many ACTIVE behaviors actually use them.  If the total > 0, then
    # the sensob needs to be updated but otherwise can be ignored.

    def markup_sensobs(self):
        for s in self.sensobs: s.add_mark()

    def markdown_sensobs(self):
        for s in self.sensobs: s.remove_mark()

    def update_activity_status(self):
        if self.active: self.consider_deactivation()
        else: self.consider_activation()

    def consider_activation(self):
        if self.do_activation_test(): self.activate()

    def consider_deactivation(self):
        if self.do_deactivation_test(): self.deactivate()

    def activate(self):
        print(self.get_name() + " " + "activate")
        self.active = True
        self.bbcon.activate_behavior(self)
        self.markup_sensobs()

    def deactivate(self):
        print(self.get_name() + " " + "deactivate")
        self.active = False
        self.bbcon.deactivate_behavior(self)
        self.markdown_sensobs()

    def update(self):
        # Use sensob data to compute motor_requests and update match_degree.  Then use match_degree to update weight.
        self.update_activity_status()
        if self.is_active():
            self.sense_and_act()
            self.update_weight()

    def update_weight(self):  self.weight = self.priority * self.match_degree

    # Determine if the behavior is currently active or not.  This needs to be subclassed for each behavior.
    def do_activation_test(self): return True
    def do_deactivation_test(self): return False

    # This is the core method for behavior computation; it needs to be subclassed.
    #  It's main jobs are a) read sensors, b) update the behavior's match_degree, c) set the motor requests.

    def sense_and_act(self): return True

    def get_name(self):
        return self.name

# This is a very basic behavior that does NOT involve any sensors.  It just keeps track of timesteps and requests a
# halt when the maximum number of steps have been reached.

class Step_Limit_Halt(Behavior):

    def __init__(self,bbcon,msteps=1000,sensobs=[],act=True,pri=1.0):
        Behavior.__init__(self,bbcon,sensobs=sensobs,act=act,pri=pri)
        self.maxsteps = msteps
        self.currstep = 0

    def sense_and_act(self):
        self.currstep += 1
        if self.currstep > self.maxsteps:
            self.request_halt()
            self.set_match_degree(1.0)
        else: self.set_match_degree(0)


# ****** SENSOB - Sensor Object *********
# Interface between a BBCON and the actual sensors of an agent.  Each sensob is associated with a single sensor, which
# may be as simple as a button or infrared sensor, or as complicated as a camera (whose "value" would be the
# complete picture, which would probably be handled by a subclass of Sensob designed specifically for cameras.

class Sensob():

    def __init__(self,sensor):
        self.mark = 0
        self.sensor = sensor
        self.value = None # Can be a scalar, vector or array

    # Marks keep track of how many ACTIVE behaviors require this sensob.  When 0, the sensob is inactive, so there
    # is no need to update the corresponding sensor (unless the sensor has HISTORY as part of its state, which I
    # assume will not happen in this system).

    def add_mark(self): self.mark += 1
    def remove_mark(self): self.mark -= 1

    def is_active(self):  return self.mark > 0
    def get_value(self):  return self.value

    def update(self):
        if self.is_active():
            self.sensor.update()
            self.value = self.sensor.get_value()

    def reset(self):
        self.sensor.reset()
        self.value = None

#********* MOTOB (Motor Object) *************
# Interface between the BBCON and the motors.
# For now, we assume that a) motobs are always active, and b) every behavior produces a motor request
# that includes a value for every motob.  Most basic robotics examples have a pair of motor outputs and nothing more.

class Motob():

    def __init__(self,motor):
        self.motor = motor

    def set_value(self,val):
        self.motor.set_value(val)