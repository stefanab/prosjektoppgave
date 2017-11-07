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
from neuralnets import reflectance_neural_network_model2
from robot_actions import RobotActionExecutor
import tflearn
import tensorflow as tf
from rewardfunction import RewardFunction


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
        GPIO.cleanup()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    discount_factor = 0.8
    motors = Motors()
    reflectance_sensors = ReflectanceSensors(motob=motors, auto_calibrate=True)
    reward_function = LineFollowerRewardFunction(RewardFunction, reflectance_sensors)
    action_executor = RobotActionExecutor(motors)
    q_net = reflectance_neural_network_model2(n_actions=action_executor.n_actions)
    modelh = ModelHandler()

    # check if we want to load some previous model or start
    # with a fresh one
    if(len(sys.argv) > 1):
    	modelh.load(sys.argv[1], q_net)

    q_dash = q_net





    #train_y = train_y.reshape([-1, 2])
    episodes = 20
    sec_cd = 5
    experience = []
    for i in range(episodes): # epiode for loop
        print("get ready for the next episode(" + str(i) + ")...")
        for sec in range(sec_cd):
            print(sec_cd+1-sec)
            sleep(1)
        is_final_state = False
        step = 0
        reflectance_sensors.update()
        updated_state = reflectance_sensors.get_value()

        while step < 100 and not (is_final_state): #main while loop
            # Store current state
            action = -1
            print("step " + str(step))
            current_state = updated_state


            # Chose action randomly or pick best action
            if(rdm.random() > .9):

                action = rdm.randint(0,action_executor.n_actions-1)
            else:
                q_values = q_net.predict(current_state.reshape([-1, 1, 6, 1]))
                print("q_values for actions are:")
                print(q_values)

                action = pick_best_action(q_values)

            print("chosen action")
            print(action)

            # get reward for current state
            reward, is_final_state = reward_function.calculate_reward(reflectance_sensors.get_value(discrete=True, debug=False), action)

            # Do selected action (update state)
            action_executor.do_action(action)
            sleep(0.2)
            motors.stop()
            step += 1
            reflectance_sensors.update()
            updated_state = reflectance_sensors.get_value()


            # Store transition of (current_state, action, reward, updated_state)
            # Change to append if you want to store all experiences
            experience.append([current_state, action, reward, updated_state, is_final_state])

            # Select a mini-batch of transitions to train on
            chosen_experience = None
            if is_final_state:
                chosen_experience = experience[len(experience)-1]
            else:
                chosen_experience = experience[rdm.randint(0, len(experience)-1)]
            # Set target, yk, as rk if terminal state or as rk + max(Q-dash)
            yk = 0
            print("is terminal?")
            print(chosen_experience[4])
            if(chosen_experience[4]):
                yk = chosen_experience[2]
            else:
                prediction_matrix = q_dash.predict(chosen_experience[3].reshape([-1, 1, 6, 1]))
                print("q_values for actions are:")
                print(prediction_matrix[0])
                prediction = prediction_matrix[0]
                max_q_updated_state = prediction[0]
                for value in prediction:
                    if value > max_q_updated_state:
                        max_q_updated_state = value

                yk = chosen_experience[2] + discount_factor * max_q_updated_state
            print("reward")
            print(chosen_experience[2])
            print("yk")
            print(yk)
            # train network
                # Predict network and set all target labels for non-chosen action
                # equal to prediction
            targets = q_net.predict(chosen_experience[0].reshape([-1, 1, 6, 1]))
            # print("targets")
            # print(targets)

            targets[0, chosen_experience[1]] = yk
                # Set target value for chosen action equal to yk minus the q_values
                #predicted by net and s
            # print("modi targets")
            # print(targets)
                # Square this value

                # update q_net

            q_net.fit(chosen_experience[0].reshape([-1, 1, 6, 1]), targets, n_epoch=1)

            # if enough time as passed set Q-dash to current q_net
            if(step % 1 == 0):
                q_dash = q_net

        #end main while
    #end episode for loop


    motors.stop()

    modelh.save("reflectance_reinforcement2.model", q_net, overwrite=True)
    GPIO.cleanup()
    sys.exit(0)

    print("done")













if __name__ == '__main__':
    __main__()
