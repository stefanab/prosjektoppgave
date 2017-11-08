#!/usr/bin/env python
from time import sleep
import signal
import sys
import random as rdm
import RPi.GPIO as GPIO
from robot.reflectance_sensors import ReflectanceSensors
from robot.motors import Motors
from robot.camera import Camera
from filehandle.modelHandler import ModelHandler
from line_follower_reward_function import LineFollowerRewardFunction
from neuralnets import reflectance_neural_network_model2
import neuralnets
from robot_actions import RobotActionExecutor
import tflearn
import tensorflow as tf
from rewardfunction import RewardFunction
import constparimg as cpi
import numpy as np

def pick_best_action(q_values_matrix):
    q_values = q_values_matrix[0]
    max_action = 0
    previous_max = q_values[0]
    print(q_values.shape)
    for i in range(len(q_values)):
        if(q_values[i] > q_values[max_action]):
            max_action = i

    return max_action

def __main__():
    #initialize all components
    def signal_handler(signal, frame):
        motors.stop()
        camera.close()
        GPIO.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    discount_factor = 0.8

    motors = Motors()
    camera = Camera()
    reflectance_sensors = ReflectanceSensors(motob=motors, auto_calibrate=True)

    constant            = cpi.constantParametersImage()

    reward_function     = LineFollowerRewardFunction(RewardFunction, reflectance_sensors)
    action_executor     = RobotActionExecutor(motors)
    q_net, name         = neuralnets.conv_reflectance_neural_network_model1(n_actions=action_executor.n_actions)

    modelh = ModelHandler()

    # check if we want to load some previous model or start
    # with a fresh one
    if(len(sys.argv) > 1):
    	modelh.load(sys.argv[1], q_net)

    q_dash = q_net





    #train_y = train_y.reshape([-1, 2])
    episodes = 20
    max_step = 10000
    sec_cd = 5
    experience = []
    for i in range(episodes): # epiode for loop
        motors.stop()
        print("get ready for the next episode(" + str(i) + ")...")
        print(sec_cd)
        sleep(sec_cd)
        is_final_state = False
        step = 0
        reflectance_sensors.update()
        updated_ref_state = reflectance_sensors.get_value()
        camera.update()
        updated_cam_state = camera.get_value()

        while step < max_step and not (is_final_state): #main while loop
            # Store current state
            action = -1
            print("step " + str(step))
            print(updated_ref_state)
            current_ref_state = updated_ref_state
            current_cam_state = updated_cam_state

            # Chose action randomly or pick best action
            was_random = True
            if(rdm.random() > .9 and False):

                action = rdm.randint(0,action_executor.n_actions-1)
            else:
                q_values = q_net.predict({'reflectance_input': current_ref_state.reshape([-1, 6]), 'image_input': current_cam_state.reshape([-1, constant.height, constant.width, constant.channels])})
                print("q_values for actions are:")
                print(q_values)
                was_random = False
                action = np.argmax(q_values)


            # get reward for current state
            reward, is_final_state = reward_function.calculate_reward(reflectance_sensors.get_value(discrete=True, debug=False), action, was_random)

            # Do selected action (update state)
            action_executor.do_action(action)
            sleep(0.051)
            motors.stop()
            step += 1

            reflectance_sensors.update()
            camera.update()
            updated_ref_state = reflectance_sensors.get_value()
            updated_cam_state = camera.get_value()

            # Store transition of (current_state, action, reward, updated_state)
            # Change to append if you want to store all experiences
            experience.append([current_ref_state, action, reward, updated_ref_state, is_final_state, current_cam_state, updated_cam_state])

            # Select a mini-batch of transitions to train on
            chosen_experience = None
            if is_final_state:
                chosen_experience = experience[len(experience)-1]
            else:
                chosen_experience = experience[rdm.randint(0, len(experience)-1)]
            # Set target, yk, as rk if terminal state or as rk + max(Q-dash)
            yk = 0

            if(chosen_experience[4]):
                yk = chosen_experience[2]
            else:
                prediction_matrix = q_dash.predict(
                {'reflectance_input': chosen_experience[3].reshape([-1, 6]),
                'image_input': chosen_experience[6].reshape([-1, constant.height, constant.width, constant.channels])}
                )
                prediction = prediction_matrix[0]
                max_q_updated_state = np.amax(prediction)


                yk = chosen_experience[2] + discount_factor * max_q_updated_state


            print("yk")
            print(yk)
            # train network
                # Predict network and set all target labels for non-chosen action
                # equal to prediction
            targets = q_net.predict(
            {'reflectance_input': chosen_experience[0].reshape([-1, 6]),
            'image_input': chosen_experience[5].reshape([-1, constant.height, constant.width, constant.channels])}
            )
            # print("targets")
            # print(targets)

            targets[0, chosen_experience[1]] = yk
                # Set target value for chosen action equal to yk minus the q_values
                #predicted by net and s
            # print("modi targets")
            # print(targets)
                # Square this value

                # update q_net
            if(i <= 0 and step <= 1):
                motors.stop()
            q_net.fit(
            {'reflectance_input': chosen_experience[0].reshape([-1, 6]),
            'image_input': chosen_experience[5].reshape([-1, constant.height, constant.width, constant.channels])}
            ,targets, n_epoch=1)
            # if enough time as passed set Q-dash to current q_net
            if(step % 1 == 0):
                q_dash = q_net

        #end main while
    #end episode for loop


    motors.stop()
    overwrite = False
    if(len(sys.argv) > 2):
        if(sys.argv[2] == 'o'):
            overwrite = True
    modelh.save(name + ".model", q_net, overwrite = overwrite)
    camera.close()
    GPIO.cleanup()
    sys.exit(0)

    print("done")













if __name__ == '__main__':
    __main__()
