




def RewardFunction():

    def __init__(self, name):
        self.name            = name
        self.state           = None
        self.previous_state  = None
        self.previous_reward = None


    def get_state(self): return self.state
    def get_previous_state(self): return self.previous_state
    def get_previous_reward(self): return self.previous_reward

    # Should calculate the reward given the current state, action (and)
    # possibly previous state
    def calculate_reward(self, state, action): return reward
