


class Trainer():

    def __init__(self, net_model):
        self.experience = []
        self.q_dash = net_model


    def train(self, q_net, experience, batch_size=10):
        self.experience.append(experience)

        target_outputs  = []
        cam_inputs      = []
        ref_inputs      = []

        # Select a mini-batch of transitions to train on
        for sample in range(batch_size):
            chosen_experience = self.experience[rdm.randint(0, len(self.experience)-1)]

            # Set target, yk, as rk if terminal state or as rk + max(Q-dash)

            yk = chosen_experience[1]

            if not chosen_experience[4]:

                prediction_matrix = self.q_dash.predict(
                {'reflectance_input': chosen_experience[3].reshape([-1, 6]),
                'image_input': chosen_experience[6].reshape([-1, constant.height, constant.width, constant.channels])}
                )
                prediction = prediction_matrix[0]
                max_q_updated_state = np.amax(prediction)


                yk += discount_factor * max_q_updated_state


            print("yk")
            print(yk)
            # train network
                # Predict network and set all target labels for non-chosen action
                # equal to prediction
            targets = q_net.predict(
            {'reflectance_input': chosen_experience[2].reshape([-1, 6]),
            'image_input': chosen_experience[5].reshape([-1, constant.height, constant.width, constant.channels])}
            )
            # print("targets")
            # print(targets)

            targets[0, chosen_experience[1]] = yk
            print(targets)
                # Set target value for chosen action equal to yk minus the q_values
                #predicted by net and s
            # print("modi targets")
            # print(targets)
                # Square this value

                # update q_net
        #end batch generation for loop
        ref_inputs.append([chosen_experience[2].reshape([-1, 6])])
        cam_inputs.append([chosen_experience[5].reshape([-1, constant.height, constant.width, constant.channels])])
        target_outputs.append(targets)
        if(i <= 0 and step <= 1):
            motors.stop()
        q_net.fit(
        {'reflectance_input': ref_inputs,
        'image_input': cam_inputs}
        ,{'targets': target_outputs}, n_epoch=1)
        # if enough time as passed set Q-dash to current q_net
        if(step % 5 == 0):
            self.q_dash = q_net
