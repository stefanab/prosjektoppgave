#!/usr/bin/env python
from time import sleep
import signal
import sys
import random as rdm
import tflearn
import tensorflow as tf
import numpy as np
from experiencehandle.experiencehandler import ExperienceHandler


class Trainer():

    def __init__(self, net_model, constant, n_actions=3):
        self.n_actions = n_actions
        self.constant   = constant
        self.experiences = []
        self.q_dash = net_model


    def save_experiences_to_file(self):
        exp_handler = ExperienceHandler()

        print("length exp")
        print(len(self.experiences))
        self.experiences = np.array(self.experiences, dtype=object)
        exp_handler.save_experiences_to_file(self.experiences)

    def simulate_training(self, experiences, q_net, motors=None, q_dash_update=10, batch_size=64, n_epochs=5000):

        discount_factor = 0.8
        if(len(experiences) < 2*batch_size):
            batch_size = 1
        # Select a mini-batch of transitions to train on
        for epoch in range(n_epochs):
            target_outputs  = []
            cam_inputs      = []
            ref_inputs      = []
            for sample in range(batch_size):
                chosen_experience = experiences[rdm.randint(0, len(experiences)-1)]

                # Set target, yk, as rk if terminal state or as rk + max(Q-dash)

                yk = chosen_experience[1]

                if not chosen_experience[4]:

                    prediction_matrix = self.q_dash.predict(
                    {'reflectance_input': chosen_experience[3].reshape([-1, 6]),
                    'image_input': chosen_experience[6].reshape([-1, self.constant.height, self.constant.width, self.constant.channels])}
                    )
                    prediction = prediction_matrix[0]
                    max_q_updated_state = np.amax(prediction)
                    if epoch % 100 == 0:
                        print("max q")
                        print(max_q_updated_state)
                    yk += discount_factor * max_q_updated_state



                # train network
                    # Predict network and set all target labels for non-chosen action
                    # equal to prediction
                targets = q_net.predict(
                {'reflectance_input': chosen_experience[2].reshape([-1, 6]),
                'image_input': chosen_experience[5].reshape([-1, self.constant.height, self.constant.width, self.constant.channels])}
                )
                if epoch % 100 == 0:
                    print("ref state")
                    print(chosen_experience[2])
                    print("diff")
                    temp_targets = targets
                    print(targets)


                targets[0, chosen_experience[0]] = yk
                if epoch % 100 == 0:
                    print(targets)
                    print(yk)

                    # Set target value for chosen action equal to yk minus the q_values
                    #predicted by net and s
                # print("modi targets")
                # print(targets)
                    # Square this value

                    # update q_net
                ref_inputs.append([chosen_experience[2].reshape([-1, 6])])
                cam_inputs.append([chosen_experience[5].reshape([-1, self.constant.height, self.constant.width, self.constant.channels])])
                target_outputs.append(targets)
                #end batch generation for loop

            ref_inputs = np.array(ref_inputs).reshape([-1, 6])
            cam_inputs = np.array(cam_inputs).reshape([-1, self.constant.height, self.constant.width, self.constant.channels])
            target_outputs = np.array(target_outputs).reshape([-1, self.n_actions])


            q_net.fit(
            {'reflectance_input': ref_inputs,
            'image_input': cam_inputs}
            ,{'targets': target_outputs}, n_epoch=1)
            # if enough time as passed set Q-dash to current q_net
            if(epoch+1 % q_dash_update == 0):
                print("update dash")
                self.q_dash = q_net

            #end epoch training loop
        return q_net

    def train(self, q_net, experience, step, i, discount_factor, motors=None, batch_size=10):
        self.experiences.append(experience)

        target_outputs  = []
        cam_inputs      = []
        ref_inputs      = []
        if(len(self.experiences) < 2*batch_size):
            batch_size = 1
        # Select a mini-batch of transitions to train on
        for sample in range(batch_size):
            chosen_experience = self.experiences[rdm.randint(0, len(self.experiences)-1)]

            # Set target, yk, as rk if terminal state or as rk + max(Q-dash)

            yk = chosen_experience[1]

            if not chosen_experience[4]:

                prediction_matrix = self.q_dash.predict(
                {'reflectance_input': chosen_experience[3].reshape([-1, 6]),
                'image_input': chosen_experience[6].reshape([-1, self.constant.height, self.constant.width, self.constant.channels])}
                )
                prediction = prediction_matrix[0]
                max_q_updated_state = np.amax(prediction)


                yk += discount_factor * max_q_updated_state



            # train network
                # Predict network and set all target labels for non-chosen action
                # equal to prediction
            targets = q_net.predict(
            {'reflectance_input': chosen_experience[2].reshape([-1, 6]),
            'image_input': chosen_experience[5].reshape([-1, self.constant.height, self.constant.width, self.constant.channels])}
            )
            if sample == 1:
                print("yk")
                print(yk)
                print("targets")
                print(targets)
            # print(targets)

            targets[0, chosen_experience[0]] = yk

                # Set target value for chosen action equal to yk minus the q_values
                #predicted by net and s
            # print("modi targets")
            # print(targets)
                # Square this value

                # update q_net
            ref_inputs.append([chosen_experience[2].reshape([-1, 6])])
            cam_inputs.append([chosen_experience[5].reshape([-1, self.constant.height, self.constant.width, self.constant.channels])])
            target_outputs.append(targets)
            #end batch generation for loop

        ref_inputs = np.array(ref_inputs).reshape([-1, 6])
        cam_inputs = np.array(cam_inputs).reshape([-1, self.constant.height, self.constant.width, self.constant.channels])
        target_outputs = np.array(target_outputs).reshape([-1, self.n_actions])
        if(i <= 0 and step <= 1 and motors != None):
            motors.stop()
        q_net.fit(
        {'reflectance_input': ref_inputs,
        'image_input': cam_inputs}
        ,{'targets': target_outputs}, n_epoch=1)
        # if enough time as passed set Q-dash to current q_net
        if(step % 5 == 0):
            self.q_dash = q_net

        return q_net
