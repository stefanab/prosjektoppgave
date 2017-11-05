#!/usr/bin/env python
from time import sleep
import signal
import sys
import random as rdm
import RPi.GPIO as GPIO
from robot.reflectance_sensors import ReflectanceSensors
from robot.motors import Motors
from filehandle.modelHandler import ModelHandler
from line_follower_reward_function import LineFollowerRewardFunction
from neuralnets import reflectance_neural_network_model
from robot_actions import RobotActionExecutor
import tflearn
import tensorflow as tf


def pick_best_action(q_values):
    max_action = 0
    previous_max = q_values[0]
    for i in range(len(q_values)):
        if(q_values[i] > q_values[max_action]):
            max_action = i

    return max_action

def __main__():
    #initialize all components
    motors = Motors()
    reflectance_sensors = ReflectanceSensors(motob=motors)
    reward_function = LineFollowerRewardFunction()
    action_executor = RobotActionExecutor(motors)
    q_net = reflectance_neural_network_model()
    q_dash = q_net
    # check if we want to load some previous model or start
    # with a fresh one
    if(len(sys.argv) > 1):
    	q_net.load(sys.argv[1])

    is_final_state = False
    step = 0
    reflectance_sensors.update()
    updated_state = reflectance_sensors.get_value()
    experience = []

    while not is_final_state and step < 200:
        # Store current state
        action = 4
        print("step " + str(step))
        current_state = updated_state
        print(current_state)

        # Chose action randomly or pick best action
        if(rdm.random() > .9):
            action = rdm.randint(0,7)
        else:
            q_values = q_net.predict(current_state)
            print("q_values for actions are:")
            print(q_values)

            action = pick_best_action(q_values)

        print("chosen action")
        print(action)

        # get reward for current state
        reward, is_final_state = reward_function.calculate_reward(current_state)

        # Do selected action (update state)
        action_executor.do_action(action)
        sleep(0.2)
        iter += 1
        reflectance_sensors.update()
        updated_state = reflectance_sensors.get_value()

        # Store transition of (current_state, action, reward, updated_state)
        # Change to append if you want to store all experiences
        experience = [current_state, action, reward, updated_state, is_final_state]

        # Select a mini-batch of transitions to train on
        chosen_experience = experience[rdm.randint(0, len(experience)-1)]

        # Set target, yk, as rk if terminal state or as rk + max(Q-dash)
        yk = 0
        if(chosen_experience[4]):
            yk = chosen_experience[2]
        else:
            prediction = q_dash.predict(chosen_experience[3])
            print("q_values for actions are:")
            print(q_values)

            max_q_updated_state = prediction[0]
            for value in prediction:
                if value > max_q_updated_state:
                    max_q_updated_state = value

            yk = chosen_experience[2] + discount_factor * max_q_updated_state

        # train network
            # Predict network and set all target labels for non-chosen action
            # equal to prediction
        targets = q_net.predict(chosen_experience[0])
        target_action = targets[chosen_experience[1]]
        targets[chosen_experience[1]] = (yk - target_action)**2
            # Set target value for chosen action equal to yk minus the q_values
            #predicted by net and s

            # Square this value

            # update q_net
        q_net.fit(chosen_experience[0], targets)

        # if enough time as passed set Q-dash to current q_net
        if(iter % 1 == 0):
            q_dash = q_net

    #end main while
















if __name__ == '__main__':
    __main__()
