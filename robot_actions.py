from robot.motors import Motors



class RobotActionExecutor():

    def __init__(self, motors, number_of_actions=8):
        self.number_of_actions = 8
        self.motors = motors



    # Action number:
    # 0-2 is left turn
    # 3 is forward
    # 4 is stop
    # 5-7 is right turn
    # default is to stop
    def do_action(self, action_number):
        if action_number == 0:
            self.motors.set_value([0, 400])
        elif action_number == 1:
            self.motors.set_value([150, 400])
        elif action_number == 2:
            self.motors.set_value([300, 400])
        elif action_number == 3:
            self.motors.set_value([250, 250])
        elif action_number == 4:
            self.motors.set_value([0, 0])
        elif action_number == 5:
            self.motors.set_value([400, 300])
        elif action_number == 6:
            self.motors.set_value([400, 150])
        elif action_number == 7:
            self.motors.set_value([400, 0])
        else:
            self.motors.set_value([0, 0]) 
