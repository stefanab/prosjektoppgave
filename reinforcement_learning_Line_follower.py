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
import neuralnets
from robot_actions import RobotActionExecutor
import tflearn
import tensorflow as tf
from rewardfunction import RewardFunction
import constparimg as cpi
import numpy as np
from trainer import Trainer

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
        print("free resources")
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
    q_net, name         = neuralnets.conv_reflectance_neural_network_model2(n_actions=action_executor.n_actions)

    trainer = Trainer(q_net, constant, n_actions=action_executor.n_actions)
    modelh = ModelHandler()

    # check if we want to load some previous model or start
    # with a fresh one
    if(len(sys.argv) > 1):
        modelh.load(sys.argv[1], q_net)

    q_dash = q_net

    test1 = [[0, 1, 2, 3]]
    test2 = [[4,5,6]]
    test3 = tf.concat([test1, test2], axis=1)
    print("concated")
    print(test3)

    #train_y = train_y.reshape([-1, 2])
    episodes = 50
    max_step = 1000
    sec_cd = 5
    experience = []
    training = True
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
            if(rdm.random() < (.1+(1/(1+step*i))) and training):

                action = rdm.randint(0,action_executor.n_actions-1)
            else:
                q_values = q_net.predict({
                'reflectance_input': current_ref_state.reshape([-1, 6]),
                'image_input': current_cam_state.reshape([-1, constant.height, constant.width, constant.channels])})
                print("q_values for actions are:")
                print(q_values)
                was_random = False
                action = np.argmax(q_values)
            #end random if-else

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
            if(training):
                q_net = trainer.train(q_net, [ action, reward, current_ref_state, updated_ref_state, is_final_state, current_cam_state, updated_cam_state], step, i, motors=motors, discount_factor)


        #end main while
    #end episode for loop
    if(training):
        print("save from main")
        trainer.save_experiences_to_file()

    motors.stop()
    overwrite = False
    if(len(sys.argv) > 2):
        if(sys.argv[2] == 'o'):
            overwrite = True

    modelh.save(name + ".model", q_net, overwrite = overwrite)


    print("free resources")
    motors.stop()
    camera.close()
    GPIO.cleanup()
    sys.exit(0)

    print("done")













if __name__ == '__main__':
    __main__()
