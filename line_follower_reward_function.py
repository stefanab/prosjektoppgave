from rewardfunction import RewardFunction
from robot.reflectance_sensors import ReflectanceSensors

# Calculates the rewards for each action in a state
# There are 2^6 different states as each state is represented as
# a black(dark) or white(light) reading from the reflectance sensors

# The reward function should give a reward of 0 as long as the robot
# stays on the line (ay least one of the readings is zero).
# If the robot goes off the line (all readings white) there is a
# negative reward of -50
# If the robot finds a spot with all black values the reward is 10
# There are 8 actions in total:
# 3 levels of left/right turn
# stop and forward

# Additional implementation:
# If the previous state was a all black state, the reward for finding
# a new all black state (essentially doing stop in all black state)
# is negative -20
class LineFollowerRewardFunction(RewardFunction):

    def __init__(self, name, reflectance_sensors):
        RewardFunction.__init__(self, name)
        self.reflectance_sensors = reflectance_sensors


    # Method to calculate rewards based on actions taken
    # state the discrete colors of the state currrently in.
    # Also return whether this state is final
    def calculate_reward(self, state, action, was_random):
        reward = 0
        
        sum_white = 0
        for reading in state:
           if reading == 1:
                sum_white += 1
        
        
        if sum_white ==  6:
            
            if not was_random:
                return reward - 50, True
            return reward - 5, True
        elif sum_white == 0:
            return reward + 1, False
        else:
            return reward + 0, False
